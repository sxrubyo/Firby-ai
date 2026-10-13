/**
 * ShapeBlur Runtime - React Bits (WebGL / Three.js Shader)
 * Scoped strictly to Final CTA Banner: #contacto .cta-final-card
 */

(function initShapeBlur() {
  function setup() {
    var ctaCard = document.querySelector('.cta-final-card, #contacto .cta-final-card');
    if (!ctaCard) return;
    if (ctaCard.querySelector('.shape-blur-canvas')) return;

    // Inject styles
    var styleId = 'shape-blur-css';
    if (!document.getElementById(styleId)) {
      var style = document.createElement('style');
      style.id = styleId;
      style.textContent = `
        .cta-final-card > .shape-blur-canvas,
        .shape-blur-canvas {
          position: absolute !important;
          inset: 0 !important;
          width: 100% !important;
          height: 100% !important;
          pointer-events: none !important;
          z-index: 2 !important;
          transition: opacity 0.5s ease;
        }

        html:not(.dark) .shape-blur-canvas {
          opacity: 0.40;
          mix-blend-mode: normal;
        }

        html.dark .shape-blur-canvas,
        html[data-theme="dark"] .shape-blur-canvas {
          opacity: 0.75;
          mix-blend-mode: screen;
        }
      `;
      document.head.appendChild(style);
    }

    var canvas = document.createElement('canvas');
    canvas.className = 'shape-blur-canvas';
    canvas.style.setProperty('position', 'absolute', 'important');
    canvas.style.setProperty('top', '0', 'important');
    canvas.style.setProperty('left', '0', 'important');
    canvas.style.setProperty('width', '100%', 'important');
    canvas.style.setProperty('height', '100%', 'important');
    canvas.style.setProperty('pointer-events', 'none', 'important');
    canvas.style.setProperty('z-index', '2', 'important');
    // Insert after iridescence canvas or as second child
    var iridCanvas = ctaCard.querySelector('.iridescence-canvas');
    if (iridCanvas && iridCanvas.nextSibling) {
      ctaCard.insertBefore(canvas, iridCanvas.nextSibling);
    } else {
      ctaCard.insertBefore(canvas, ctaCard.firstChild);
    }

    var gl = canvas.getContext('webgl2', { antialias: true, alpha: true }) ||
             canvas.getContext('webgl', { antialias: true, alpha: true });
    if (!gl) return;

    if (gl.getExtension) {
      gl.getExtension('OES_standard_derivatives');
    }

    var isWebGL2 = typeof WebGL2RenderingContext !== 'undefined' && gl instanceof WebGL2RenderingContext;

    var vsSource = isWebGL2 ? `#version 300 es
      in vec2 position;
      out vec2 v_texcoord;
      void main() {
        v_texcoord = (position + 1.0) * 0.5;
        gl_Position = vec4(position, 0.0, 1.0);
      }
    ` : `
      attribute vec2 position;
      varying vec2 v_texcoord;
      void main() {
        v_texcoord = (position + 1.0) * 0.5;
        gl_Position = vec4(position, 0.0, 1.0);
      }
    `;

    var fsSource = isWebGL2 ? `#version 300 es
      precision highp float;
      in vec2 v_texcoord;
      out vec4 fragColor;

      uniform vec3 u_color;
      uniform vec2 u_mouse;
      uniform vec2 u_resolution;
      uniform float u_pixelRatio;
      uniform float u_shapeSize;
      uniform float u_roundness;
      uniform float u_borderSize;
      uniform float u_circleSize;
      uniform float u_circleEdge;

      #define PI 3.14159265358979323846
      #define TWO_PI 6.2831853071795864

      vec2 coord(in vec2 p) {
        p = p / u_resolution.xy;
        if (u_resolution.x > u_resolution.y) {
          p.x *= u_resolution.x / u_resolution.y;
          p.x += (u_resolution.y - u_resolution.x) / u_resolution.y / 2.0;
        } else {
          p.y *= u_resolution.y / u_resolution.x;
          p.y += (u_resolution.x - u_resolution.y) / u_resolution.x / 2.0;
        }
        p -= 0.5;
        p *= vec2(-1.0, 1.0);
        return p;
      }

      #define st0 coord(gl_FragCoord.xy)
      #define mx coord(u_mouse * u_pixelRatio)

      float sdRoundRect(vec2 p, vec2 b, float r) {
        vec2 d = abs(p - 0.5) * 4.2 - b + vec2(r);
        return min(max(d.x, d.y), 0.0) + length(max(d, 0.0)) - r;
      }

      float sdCircle(in vec2 st, in vec2 center) {
        return length(st - center) * 2.0;
      }

      float fill(float x, float size, float edge) {
        return 1.0 - smoothstep(size - edge, size + edge, x);
      }

      float strokeAA(float x, float size, float w, float edge) {
        float afwidth = length(vec2(dFdx(x), dFdy(x))) * 0.70710678;
        float d = smoothstep(size - edge - afwidth, size + edge + afwidth, x + w * 0.5)
                - smoothstep(size - edge - afwidth, size + edge + afwidth, x - w * 0.5);
        return clamp(d, 0.0, 1.0);
      }

      void main() {
        vec2 st = st0 + 0.5;
        vec2 posMouse = mx * vec2(1.0, -1.0) + 0.5;

        float sdfCircle = fill(
          sdCircle(st, posMouse),
          u_circleSize,
          u_circleEdge
        );

        float sdf = sdRoundRect(st, vec2(u_shapeSize), u_roundness);
        sdf = strokeAA(sdf, 0.0, u_borderSize, sdfCircle) * 4.0;

        float alpha = clamp(sdf, 0.0, 1.0);
        fragColor = vec4(u_color, alpha);
      }
    ` : `
      #extension GL_OES_standard_derivatives : enable
      precision highp float;
      varying vec2 v_texcoord;

      uniform vec3 u_color;
      uniform vec2 u_mouse;
      uniform vec2 u_resolution;
      uniform float u_pixelRatio;
      uniform float u_shapeSize;
      uniform float u_roundness;
      uniform float u_borderSize;
      uniform float u_circleSize;
      uniform float u_circleEdge;

      #define PI 3.14159265358979323846
      #define TWO_PI 6.2831853071795864

      vec2 coord(in vec2 p) {
        p = p / u_resolution.xy;
        if (u_resolution.x > u_resolution.y) {
          p.x *= u_resolution.x / u_resolution.y;
          p.x += (u_resolution.y - u_resolution.x) / u_resolution.y / 2.0;
        } else {
          p.y *= u_resolution.y / u_resolution.x;
          p.y += (u_resolution.x - u_resolution.y) / u_resolution.x / 2.0;
        }
        p -= 0.5;
        p *= vec2(-1.0, 1.0);
        return p;
      }

      #define st0 coord(gl_FragCoord.xy)
      #define mx coord(u_mouse * u_pixelRatio)

      float sdRoundRect(vec2 p, vec2 b, float r) {
        vec2 d = abs(p - 0.5) * 4.2 - b + vec2(r);
        return min(max(d.x, d.y), 0.0) + length(max(d, 0.0)) - r;
      }

      float sdCircle(in vec2 st, in vec2 center) {
        return length(st - center) * 2.0;
      }

      float fill(float x, float size, float edge) {
        return 1.0 - smoothstep(size - edge, size + edge, x);
      }

      float strokeAA(float x, float size, float w, float edge) {
        float afwidth = length(vec2(dFdx(x), dFdy(x))) * 0.70710678;
        float d = smoothstep(size - edge - afwidth, size + edge + afwidth, x + w * 0.5)
                - smoothstep(size - edge - afwidth, size + edge + afwidth, x - w * 0.5);
        return clamp(d, 0.0, 1.0);
      }

      void main() {
        vec2 st = st0 + 0.5;
        vec2 posMouse = mx * vec2(1.0, -1.0) + 0.5;

        float sdfCircle = fill(
          sdCircle(st, posMouse),
          u_circleSize,
          u_circleEdge
        );

        float sdf = sdRoundRect(st, vec2(u_shapeSize), u_roundness);
        sdf = strokeAA(sdf, 0.0, u_borderSize, sdfCircle) * 4.0;

        float alpha = clamp(sdf, 0.0, 1.0);
        gl_FragColor = vec4(u_color, alpha);
      }
    `;

    function compile(type, src) {
      var s = gl.createShader(type);
      gl.shaderSource(s, src);
      gl.compileShader(s);
      return s;
    }

    var prog = gl.createProgram();
    gl.attachShader(prog, compile(gl.VERTEX_SHADER, vsSource));
    gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, fsSource));
    gl.linkProgram(prog);
    gl.useProgram(prog);

    var buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
      -1, -1,
       1, -1,
      -1,  1,
      -1,  1,
       1, -1,
       1,  1
    ]), gl.STATIC_DRAW);

    var posLoc = gl.getAttribLocation(prog, isWebGL2 ? 'position' : 'position');
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

    var uColorLoc = gl.getUniformLocation(prog, 'u_color');
    var uMouseLoc = gl.getUniformLocation(prog, 'u_mouse');
    var uResLoc = gl.getUniformLocation(prog, 'u_resolution');
    var uPixelRatioLoc = gl.getUniformLocation(prog, 'u_pixelRatio');
    var uShapeSizeLoc = gl.getUniformLocation(prog, 'u_shapeSize');
    var uRoundnessLoc = gl.getUniformLocation(prog, 'u_roundness');
    var uBorderSizeLoc = gl.getUniformLocation(prog, 'u_borderSize');
    var uCircleSizeLoc = gl.getUniformLocation(prog, 'u_circleSize');
    var uCircleEdgeLoc = gl.getUniformLocation(prog, 'u_circleEdge');

    var dpr = 1;
    var mouseX = 0, mouseY = 0;
    var mouseDampX = 0, mouseDampY = 0;

    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      var w = ctaCard.offsetWidth;
      var h = ctaCard.offsetHeight;
      if (w === 0 || h === 0) return;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      gl.viewport(0, 0, canvas.width, canvas.height);

      gl.useProgram(prog);
      gl.uniform2f(uResLoc, canvas.width, canvas.height);
      gl.uniform1f(uPixelRatioLoc, dpr);
      // Props from example: shapeSize=0.5, roundness=0.5, borderSize=0.05, circleSize=0.5, circleEdge=1
      gl.uniform1f(uShapeSizeLoc, 0.5);
      gl.uniform1f(uRoundnessLoc, 0.5);
      gl.uniform1f(uBorderSizeLoc, 0.05);
      gl.uniform1f(uCircleSizeLoc, 0.5);
      gl.uniform1f(uCircleEdgeLoc, 1.0);

      if (mouseX === 0 && mouseY === 0) {
        mouseX = w * 0.5;
        mouseY = h * 0.5;
        mouseDampX = mouseX;
        mouseDampY = mouseY;
      }
    }
    window.addEventListener('resize', resize, { passive: true });
    resize();

    // Mouse tracking on the card
    ctaCard.addEventListener('mousemove', function(e) {
      var rect = ctaCard.getBoundingClientRect();
      mouseX = e.clientX - rect.left;
      mouseY = e.clientY - rect.top;
    }, { passive: true });

    ctaCard.addEventListener('mouseleave', function() {
      var w = ctaCard.offsetWidth;
      var h = ctaCard.offsetHeight;
      mouseX = w * 0.5;
      mouseY = h * 0.5;
    }, { passive: true });

    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

    var isVisible = true;
    if ('IntersectionObserver' in window) {
      var obs = new IntersectionObserver(function(entries) {
        isVisible = entries[0].isIntersecting;
      }, { threshold: 0.05 });
      obs.observe(ctaCard);
    }

    var lastT = performance.now();
    function render(now) {
      if (isVisible) {
        var dt = Math.min((now - lastT) * 0.001, 0.1);
        lastT = now;

        // Damped mouse movement (matching THREE.MathUtils.damp)
        var factor = 1.0 - Math.exp(-8.0 * dt);
        mouseDampX += (mouseX - mouseDampX) * factor;
        mouseDampY += (mouseY - mouseDampY) * factor;

        var isDark = document.documentElement.classList.contains('dark') ||
                     document.documentElement.getAttribute('data-theme') === 'dark';

        gl.useProgram(prog);
        gl.uniform2f(uMouseLoc, mouseDampX, mouseDampY);
        if (isDark) {
          gl.uniform3f(uColorLoc, 0.72, 0.98, 0.0);
        } else {
          gl.uniform3f(uColorLoc, 1.0, 1.0, 1.0);
        }

        gl.clearColor(0, 0, 0, 0);
        gl.clear(gl.COLOR_BUFFER_BIT);
        gl.drawArrays(gl.TRIANGLES, 0, 6);
      }
      requestAnimationFrame(render);
    }
    requestAnimationFrame(render);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setup);
  } else {
    setup();
  }
})();
