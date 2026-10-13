var e=Object.create,t=Object.defineProperty,n=Object.getOwnPropertyDescriptor,r=Object.getOwnPropertyNames,i=Object.getPrototypeOf,a=Object.prototype.hasOwnProperty,o=(e,t)=>()=>(t||(e((t={exports:{}}).exports,t),e=null),t.exports),s=(e,i,o,s)=>{if(i&&typeof i==`object`||typeof i==`function`)for(var c=r(i),l=0,u=c.length,d;l<u;l++)d=c[l],!a.call(e,d)&&d!==o&&t(e,d,{get:(e=>i[e]).bind(null,d),enumerable:!(s=n(i,d))||s.enumerable});return e},c=(n,r,o)=>(o=n==null?{}:e(i(n)),s(r||!n||!n.__esModule||!a.call(n,`default`)?t(o,`default`,{value:n,enumerable:!0}):o,n));(function(){let e=document.createElement(`link`).relList;if(e&&e.supports&&e.supports(`modulepreload`))return;for(let e of document.querySelectorAll(`link[rel="modulepreload"]`))n(e);new MutationObserver(e=>{for(let t of e)if(t.type===`childList`)for(let e of t.addedNodes)e.tagName===`LINK`&&e.rel===`modulepreload`&&n(e)}).observe(document,{childList:!0,subtree:!0});function t(e){let t={};return e.integrity&&(t.integrity=e.integrity),e.referrerPolicy&&(t.referrerPolicy=e.referrerPolicy),t.credentials=e.crossOrigin===`use-credentials`?`include`:e.crossOrigin===`anonymous`?`omit`:`same-origin`,t}function n(e){if(e.ep)return;e.ep=!0;let n=t(e);fetch(e.href,n)}})();var l=o((e=>{var t=Symbol.for(`react.transitional.element`),n=Symbol.for(`react.portal`),r=Symbol.for(`react.fragment`),i=Symbol.for(`react.strict_mode`),a=Symbol.for(`react.profiler`),o=Symbol.for(`react.consumer`),s=Symbol.for(`react.context`),c=Symbol.for(`react.forward_ref`),l=Symbol.for(`react.suspense`),u=Symbol.for(`react.memo`),d=Symbol.for(`react.lazy`),f=Symbol.for(`react.activity`),p=Symbol.iterator;function m(e){return typeof e!=`object`||!e?null:(e=p&&e[p]||e[`@@iterator`],typeof e==`function`?e:null)}var h={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},g=Object.assign,_={};function v(e,t,n){this.props=e,this.context=t,this.refs=_,this.updater=n||h}v.prototype.isReactComponent={},v.prototype.setState=function(e,t){if(typeof e!=`object`&&typeof e!=`function`&&e!=null)throw Error(`takes an object of state variables to update or a function which returns an object of state variables.`);this.updater.enqueueSetState(this,e,t,`setState`)},v.prototype.forceUpdate=function(e){this.updater.enqueueForceUpdate(this,e,`forceUpdate`)};function y(){}y.prototype=v.prototype;function b(e,t,n){this.props=e,this.context=t,this.refs=_,this.updater=n||h}var x=b.prototype=new y;x.constructor=b,g(x,v.prototype),x.isPureReactComponent=!0;var S=Array.isArray;function C(){}var w={H:null,A:null,T:null,S:null},T=Object.prototype.hasOwnProperty;function E(e,n,r){var i=r.ref;return{$$typeof:t,type:e,key:n,ref:i===void 0?null:i,props:r}}function D(e,t){return E(e.type,t,e.props)}function O(e){return typeof e==`object`&&!!e&&e.$$typeof===t}function k(e){var t={"=":`=0`,":":`=2`};return`$`+e.replace(/[=:]/g,function(e){return t[e]})}var A=/\/+/g;function j(e,t){return typeof e==`object`&&e&&e.key!=null?k(``+e.key):t.toString(36)}function M(e){switch(e.status){case`fulfilled`:return e.value;case`rejected`:throw e.reason;default:switch(typeof e.status==`string`?e.then(C,C):(e.status=`pending`,e.then(function(t){e.status===`pending`&&(e.status=`fulfilled`,e.value=t)},function(t){e.status===`pending`&&(e.status=`rejected`,e.reason=t)})),e.status){case`fulfilled`:return e.value;case`rejected`:throw e.reason}}throw e}function N(e,r,i,a,o){var s=typeof e;(s===`undefined`||s===`boolean`)&&(e=null);var c=!1;if(e===null)c=!0;else switch(s){case`bigint`:case`string`:case`number`:c=!0;break;case`object`:switch(e.$$typeof){case t:case n:c=!0;break;case d:return c=e._init,N(c(e._payload),r,i,a,o)}}if(c)return o=o(e),c=a===``?`.`+j(e,0):a,S(o)?(i=``,c!=null&&(i=c.replace(A,`$&/`)+`/`),N(o,r,i,``,function(e){return e})):o!=null&&(O(o)&&(o=D(o,i+(o.key==null||e&&e.key===o.key?``:(``+o.key).replace(A,`$&/`)+`/`)+c)),r.push(o)),1;c=0;var l=a===``?`.`:a+`:`;if(S(e))for(var u=0;u<e.length;u++)a=e[u],s=l+j(a,u),c+=N(a,r,i,s,o);else if(u=m(e),typeof u==`function`)for(e=u.call(e),u=0;!(a=e.next()).done;)a=a.value,s=l+j(a,u++),c+=N(a,r,i,s,o);else if(s===`object`){if(typeof e.then==`function`)return N(M(e),r,i,a,o);throw r=String(e),Error(`Objects are not valid as a React child (found: `+(r===`[object Object]`?`object with keys {`+Object.keys(e).join(`, `)+`}`:r)+`). If you meant to render a collection of children, use an array instead.`)}return c}function P(e,t,n){if(e==null)return e;var r=[],i=0;return N(e,r,``,``,function(e){return t.call(n,e,i++)}),r}function F(e){if(e._status===-1){var t=e._result;t=t(),t.then(function(t){(e._status===0||e._status===-1)&&(e._status=1,e._result=t)},function(t){(e._status===0||e._status===-1)&&(e._status=2,e._result=t)}),e._status===-1&&(e._status=0,e._result=t)}if(e._status===1)return e._result.default;throw e._result}var I=typeof reportError==`function`?reportError:function(e){if(typeof window==`object`&&typeof window.ErrorEvent==`function`){var t=new window.ErrorEvent(`error`,{bubbles:!0,cancelable:!0,message:typeof e==`object`&&e&&typeof e.message==`string`?String(e.message):String(e),error:e});if(!window.dispatchEvent(t))return}else if(typeof process==`object`&&typeof process.emit==`function`){process.emit(`uncaughtException`,e);return}console.error(e)},L={map:P,forEach:function(e,t,n){P(e,function(){t.apply(this,arguments)},n)},count:function(e){var t=0;return P(e,function(){t++}),t},toArray:function(e){return P(e,function(e){return e})||[]},only:function(e){if(!O(e))throw Error(`React.Children.only expected to receive a single React element child.`);return e}};e.Activity=f,e.Children=L,e.Component=v,e.Fragment=r,e.Profiler=a,e.PureComponent=b,e.StrictMode=i,e.Suspense=l,e.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=w,e.__COMPILER_RUNTIME={__proto__:null,c:function(e){return w.H.useMemoCache(e)}},e.cache=function(e){return function(){return e.apply(null,arguments)}},e.cacheSignal=function(){return null},e.cloneElement=function(e,t,n){if(e==null)throw Error(`The argument must be a React element, but you passed `+e+`.`);var r=g({},e.props),i=e.key;if(t!=null)for(a in t.key!==void 0&&(i=``+t.key),t)!T.call(t,a)||a===`key`||a===`__self`||a===`__source`||a===`ref`&&t.ref===void 0||(r[a]=t[a]);var a=arguments.length-2;if(a===1)r.children=n;else if(1<a){for(var o=Array(a),s=0;s<a;s++)o[s]=arguments[s+2];r.children=o}return E(e.type,i,r)},e.createContext=function(e){return e={$$typeof:s,_currentValue:e,_currentValue2:e,_threadCount:0,Provider:null,Consumer:null},e.Provider=e,e.Consumer={$$typeof:o,_context:e},e},e.createElement=function(e,t,n){var r,i={},a=null;if(t!=null)for(r in t.key!==void 0&&(a=``+t.key),t)T.call(t,r)&&r!==`key`&&r!==`__self`&&r!==`__source`&&(i[r]=t[r]);var o=arguments.length-2;if(o===1)i.children=n;else if(1<o){for(var s=Array(o),c=0;c<o;c++)s[c]=arguments[c+2];i.children=s}if(e&&e.defaultProps)for(r in o=e.defaultProps,o)i[r]===void 0&&(i[r]=o[r]);return E(e,a,i)},e.createRef=function(){return{current:null}},e.forwardRef=function(e){return{$$typeof:c,render:e}},e.isValidElement=O,e.lazy=function(e){return{$$typeof:d,_payload:{_status:-1,_result:e},_init:F}},e.memo=function(e,t){return{$$typeof:u,type:e,compare:t===void 0?null:t}},e.startTransition=function(e){var t=w.T,n={};w.T=n;try{var r=e(),i=w.S;i!==null&&i(n,r),typeof r==`object`&&r&&typeof r.then==`function`&&r.then(C,I)}catch(e){I(e)}finally{t!==null&&n.types!==null&&(t.types=n.types),w.T=t}},e.unstable_useCacheRefresh=function(){return w.H.useCacheRefresh()},e.use=function(e){return w.H.use(e)},e.useActionState=function(e,t,n){return w.H.useActionState(e,t,n)},e.useCallback=function(e,t){return w.H.useCallback(e,t)},e.useContext=function(e){return w.H.useContext(e)},e.useDebugValue=function(){},e.useDeferredValue=function(e,t){return w.H.useDeferredValue(e,t)},e.useEffect=function(e,t){return w.H.useEffect(e,t)},e.useEffectEvent=function(e){return w.H.useEffectEvent(e)},e.useId=function(){return w.H.useId()},e.useImperativeHandle=function(e,t,n){return w.H.useImperativeHandle(e,t,n)},e.useInsertionEffect=function(e,t){return w.H.useInsertionEffect(e,t)},e.useLayoutEffect=function(e,t){return w.H.useLayoutEffect(e,t)},e.useMemo=function(e,t){return w.H.useMemo(e,t)},e.useOptimistic=function(e,t){return w.H.useOptimistic(e,t)},e.useReducer=function(e,t,n){return w.H.useReducer(e,t,n)},e.useRef=function(e){return w.H.useRef(e)},e.useState=function(e){return w.H.useState(e)},e.useSyncExternalStore=function(e,t,n){return w.H.useSyncExternalStore(e,t,n)},e.useTransition=function(){return w.H.useTransition()},e.version=`19.2.8`})),u=o(((e,t)=>{t.exports=l()})),d=o((e=>{function t(e,t){var n=e.length;e.push(t);a:for(;0<n;){var r=n-1>>>1,a=e[r];if(0<i(a,t))e[r]=t,e[n]=a,n=r;else break a}}function n(e){return e.length===0?null:e[0]}function r(e){if(e.length===0)return null;var t=e[0],n=e.pop();if(n!==t){e[0]=n;a:for(var r=0,a=e.length,o=a>>>1;r<o;){var s=2*(r+1)-1,c=e[s],l=s+1,u=e[l];if(0>i(c,n))l<a&&0>i(u,c)?(e[r]=u,e[l]=n,r=l):(e[r]=c,e[s]=n,r=s);else if(l<a&&0>i(u,n))e[r]=u,e[l]=n,r=l;else break a}}return t}function i(e,t){var n=e.sortIndex-t.sortIndex;return n===0?e.id-t.id:n}if(e.unstable_now=void 0,typeof performance==`object`&&typeof performance.now==`function`){var a=performance;e.unstable_now=function(){return a.now()}}else{var o=Date,s=o.now();e.unstable_now=function(){return o.now()-s}}var c=[],l=[],u=1,d=null,f=3,p=!1,m=!1,h=!1,g=!1,_=typeof setTimeout==`function`?setTimeout:null,v=typeof clearTimeout==`function`?clearTimeout:null,y=typeof setImmediate<`u`?setImmediate:null;function b(e){for(var i=n(l);i!==null;){if(i.callback===null)r(l);else if(i.startTime<=e)r(l),i.sortIndex=i.expirationTime,t(c,i);else break;i=n(l)}}function x(e){if(h=!1,b(e),!m){if(n(c)!==null)m=!0,S||(S=!0,O());else{var t=n(l);t!==null&&j(x,t.startTime-e)}}}var S=!1,C=-1,w=5,T=-1;function E(){return g?!0:!(e.unstable_now()-T<w)}function D(){if(g=!1,S){var t=e.unstable_now();T=t;var i=!0;try{a:{m=!1,h&&(h=!1,v(C),C=-1),p=!0;var a=f;try{b:{for(b(t),d=n(c);d!==null&&!(d.expirationTime>t&&E());){var o=d.callback;if(typeof o==`function`){d.callback=null,f=d.priorityLevel;var s=o(d.expirationTime<=t);if(t=e.unstable_now(),typeof s==`function`){d.callback=s,b(t),i=!0;break b}d===n(c)&&r(c),b(t)}else r(c);d=n(c)}if(d!==null)i=!0;else{var u=n(l);u!==null&&j(x,u.startTime-t),i=!1}}break a}finally{d=null,f=a,p=!1}}}finally{i?O():S=!1}}}var O;if(typeof y==`function`)O=function(){y(D)};else if(typeof MessageChannel<`u`){var k=new MessageChannel,A=k.port2;k.port1.onmessage=D,O=function(){A.postMessage(null)}}else O=function(){_(D,0)};function j(t,n){C=_(function(){t(e.unstable_now())},n)}e.unstable_IdlePriority=5,e.unstable_ImmediatePriority=1,e.unstable_LowPriority=4,e.unstable_NormalPriority=3,e.unstable_Profiling=null,e.unstable_UserBlockingPriority=2,e.unstable_cancelCallback=function(e){e.callback=null},e.unstable_forceFrameRate=function(e){0>e||125<e?console.error(`forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported`):w=0<e?Math.floor(1e3/e):5},e.unstable_getCurrentPriorityLevel=function(){return f},e.unstable_next=function(e){switch(f){case 1:case 2:case 3:var t=3;break;default:t=f}var n=f;f=t;try{return e()}finally{f=n}},e.unstable_requestPaint=function(){g=!0},e.unstable_runWithPriority=function(e,t){switch(e){case 1:case 2:case 3:case 4:case 5:break;default:e=3}var n=f;f=e;try{return t()}finally{f=n}},e.unstable_scheduleCallback=function(r,i,a){var o=e.unstable_now();switch(typeof a==`object`&&a?(a=a.delay,a=typeof a==`number`&&0<a?o+a:o):a=o,r){case 1:var s=-1;break;case 2:s=250;break;case 5:s=1073741823;break;case 4:s=1e4;break;default:s=5e3}return s=a+s,r={id:u++,callback:i,priorityLevel:r,startTime:a,expirationTime:s,sortIndex:-1},a>o?(r.sortIndex=a,t(l,r),n(c)===null&&r===n(l)&&(h?(v(C),C=-1):h=!0,j(x,a-o))):(r.sortIndex=s,t(c,r),m||p||(m=!0,S||(S=!0,O()))),r},e.unstable_shouldYield=E,e.unstable_wrapCallback=function(e){var t=f;return function(){var n=f;f=t;try{return e.apply(this,arguments)}finally{f=n}}}})),f=o(((e,t)=>{t.exports=d()})),p=o((e=>{var t=u();function n(e){var t=`https://react.dev/errors/`+e;if(1<arguments.length){t+=`?args[]=`+encodeURIComponent(arguments[1]);for(var n=2;n<arguments.length;n++)t+=`&args[]=`+encodeURIComponent(arguments[n])}return`Minified React error #`+e+`; visit `+t+` for the full message or use the non-minified dev environment for full errors and additional helpful warnings.`}function r(){}var i={d:{f:r,r:function(){throw Error(n(522))},D:r,C:r,L:r,m:r,X:r,S:r,M:r},p:0,findDOMNode:null},a=Symbol.for(`react.portal`);function o(e,t,n){var r=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:a,key:r==null?null:``+r,children:e,containerInfo:t,implementation:n}}var s=t.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE;function c(e,t){if(e===`font`)return``;if(typeof t==`string`)return t===`use-credentials`?t:``}e.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=i,e.createPortal=function(e,t){var r=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!t||t.nodeType!==1&&t.nodeType!==9&&t.nodeType!==11)throw Error(n(299));return o(e,t,null,r)},e.flushSync=function(e){var t=s.T,n=i.p;try{if(s.T=null,i.p=2,e)return e()}finally{s.T=t,i.p=n,i.d.f()}},e.preconnect=function(e,t){typeof e==`string`&&(t?(t=t.crossOrigin,t=typeof t==`string`?t===`use-credentials`?t:``:void 0):t=null,i.d.C(e,t))},e.prefetchDNS=function(e){typeof e==`string`&&i.d.D(e)},e.preinit=function(e,t){if(typeof e==`string`&&t&&typeof t.as==`string`){var n=t.as,r=c(n,t.crossOrigin),a=typeof t.integrity==`string`?t.integrity:void 0,o=typeof t.fetchPriority==`string`?t.fetchPriority:void 0;n===`style`?i.d.S(e,typeof t.precedence==`string`?t.precedence:void 0,{crossOrigin:r,integrity:a,fetchPriority:o}):n===`script`&&i.d.X(e,{crossOrigin:r,integrity:a,fetchPriority:o,nonce:typeof t.nonce==`string`?t.nonce:void 0})}},e.preinitModule=function(e,t){if(typeof e==`string`){if(typeof t==`object`&&t){if(t.as==null||t.as===`script`){var n=c(t.as,t.crossOrigin);i.d.M(e,{crossOrigin:n,integrity:typeof t.integrity==`string`?t.integrity:void 0,nonce:typeof t.nonce==`string`?t.nonce:void 0})}}else t??i.d.M(e)}},e.preload=function(e,t){if(typeof e==`string`&&typeof t==`object`&&t&&typeof t.as==`string`){var n=t.as,r=c(n,t.crossOrigin);i.d.L(e,n,{crossOrigin:r,integrity:typeof t.integrity==`string`?t.integrity:void 0,nonce:typeof t.nonce==`string`?t.nonce:void 0,type:typeof t.type==`string`?t.type:void 0,fetchPriority:typeof t.fetchPriority==`string`?t.fetchPriority:void 0,referrerPolicy:typeof t.referrerPolicy==`string`?t.referrerPolicy:void 0,imageSrcSet:typeof t.imageSrcSet==`string`?t.imageSrcSet:void 0,imageSizes:typeof t.imageSizes==`string`?t.imageSizes:void 0,media:typeof t.media==`string`?t.media:void 0})}},e.preloadModule=function(e,t){if(typeof e==`string`){if(t){var n=c(t.as,t.crossOrigin);i.d.m(e,{as:typeof t.as==`string`&&t.as!==`script`?t.as:void 0,crossOrigin:n,integrity:typeof t.integrity==`string`?t.integrity:void 0})}else i.d.m(e)}},e.requestFormReset=function(e){i.d.r(e)},e.unstable_batchedUpdates=function(e,t){return e(t)},e.useFormState=function(e,t,n){return s.H.useFormState(e,t,n)},e.useFormStatus=function(){return s.H.useHostTransitionStatus()},e.version=`19.2.8`})),m=o(((e,t)=>{function n(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>`u`||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!=`function`))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(n)}catch(e){console.error(e)}}n(),t.exports=p()})),h=o((e=>{var t=f(),n=u(),r=m();function i(e){var t=`https://react.dev/errors/`+e;if(1<arguments.length){t+=`?args[]=`+encodeURIComponent(arguments[1]);for(var n=2;n<arguments.length;n++)t+=`&args[]=`+encodeURIComponent(arguments[n])}return`Minified React error #`+e+`; visit `+t+` for the full message or use the non-minified dev environment for full errors and additional helpful warnings.`}function a(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function o(e){var t=e,n=e;if(e.alternate)for(;t.return;)t=t.return;else{e=t;do t=e,t.flags&4098&&(n=t.return),e=t.return;while(e)}return t.tag===3?n:null}function s(e){if(e.tag===13){var t=e.memoizedState;if(t===null&&(e=e.alternate,e!==null&&(t=e.memoizedState)),t!==null)return t.dehydrated}return null}function c(e){if(e.tag===31){var t=e.memoizedState;if(t===null&&(e=e.alternate,e!==null&&(t=e.memoizedState)),t!==null)return t.dehydrated}return null}function l(e){if(o(e)!==e)throw Error(i(188))}function d(e){var t=e.alternate;if(!t){if(t=o(e),t===null)throw Error(i(188));return t===e?e:null}for(var n=e,r=t;;){var a=n.return;if(a===null)break;var s=a.alternate;if(s===null){if(r=a.return,r!==null){n=r;continue}break}if(a.child===s.child){for(s=a.child;s;){if(s===n)return l(a),e;if(s===r)return l(a),t;s=s.sibling}throw Error(i(188))}if(n.return!==r.return)n=a,r=s;else{for(var c=!1,u=a.child;u;){if(u===n){c=!0,n=a,r=s;break}if(u===r){c=!0,r=a,n=s;break}u=u.sibling}if(!c){for(u=s.child;u;){if(u===n){c=!0,n=s,r=a;break}if(u===r){c=!0,r=s,n=a;break}u=u.sibling}if(!c)throw Error(i(189))}}if(n.alternate!==r)throw Error(i(190))}if(n.tag!==3)throw Error(i(188));return n.stateNode.current===n?e:t}function p(e){var t=e.tag;if(t===5||t===26||t===27||t===6)return e;for(e=e.child;e!==null;){if(t=p(e),t!==null)return t;e=e.sibling}return null}var h=Object.assign,g=Symbol.for(`react.element`),_=Symbol.for(`react.transitional.element`),v=Symbol.for(`react.portal`),y=Symbol.for(`react.fragment`),b=Symbol.for(`react.strict_mode`),x=Symbol.for(`react.profiler`),S=Symbol.for(`react.consumer`),C=Symbol.for(`react.context`),w=Symbol.for(`react.forward_ref`),T=Symbol.for(`react.suspense`),E=Symbol.for(`react.suspense_list`),D=Symbol.for(`react.memo`),O=Symbol.for(`react.lazy`),k=Symbol.for(`react.activity`),A=Symbol.for(`react.memo_cache_sentinel`),j=Symbol.iterator;function M(e){return typeof e!=`object`||!e?null:(e=j&&e[j]||e[`@@iterator`],typeof e==`function`?e:null)}var N=Symbol.for(`react.client.reference`);function P(e){if(e==null)return null;if(typeof e==`function`)return e.$$typeof===N?null:e.displayName||e.name||null;if(typeof e==`string`)return e;switch(e){case y:return`Fragment`;case x:return`Profiler`;case b:return`StrictMode`;case T:return`Suspense`;case E:return`SuspenseList`;case k:return`Activity`}if(typeof e==`object`)switch(e.$$typeof){case v:return`Portal`;case C:return e.displayName||`Context`;case S:return(e._context.displayName||`Context`)+`.Consumer`;case w:var t=e.render;return e=e.displayName,e||=(e=t.displayName||t.name||``,e===``?`ForwardRef`:`ForwardRef(`+e+`)`),e;case D:return t=e.displayName||null,t===null?P(e.type)||`Memo`:t;case O:t=e._payload,e=e._init;try{return P(e(t))}catch{}}return null}var F=Array.isArray,I=n.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,L=r.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,R={pending:!1,data:null,method:null,action:null},z=[],B=-1;function V(e){return{current:e}}function H(e){0>B||(e.current=z[B],z[B]=null,B--)}function U(e,t){B++,z[B]=e.current,e.current=t}var W=V(null),ee=V(null),te=V(null),G=V(null);function ne(e,t){switch(U(te,t),U(ee,e),U(W,null),t.nodeType){case 9:case 11:e=(e=t.documentElement)&&(e=e.namespaceURI)?Vd(e):0;break;default:if(e=t.tagName,t=t.namespaceURI)t=Vd(t),e=Hd(t,e);else switch(e){case`svg`:e=1;break;case`math`:e=2;break;default:e=0}}H(W),U(W,e)}function re(){H(W),H(ee),H(te)}function ie(e){e.memoizedState!==null&&U(G,e);var t=W.current,n=Hd(t,e.type);t!==n&&(U(ee,e),U(W,n))}function ae(e){ee.current===e&&(H(W),H(ee)),G.current===e&&(H(G),Qf._currentValue=R)}var oe,se;function ce(e){if(oe===void 0)try{throw Error()}catch(e){var t=e.stack.trim().match(/\n( *(at )?)/);oe=t&&t[1]||``,se=-1<e.stack.indexOf(`
    at`)?` (<anonymous>)`:-1<e.stack.indexOf(`@`)?`@unknown:0:0`:``}return`
`+oe+e+se}var le=!1;function ue(e,t){if(!e||le)return``;le=!0;var n=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{var r={DetermineComponentFrameRoot:function(){try{if(t){var n=function(){throw Error()};if(Object.defineProperty(n.prototype,"props",{set:function(){throw Error()}}),typeof Reflect==`object`&&Reflect.construct){try{Reflect.construct(n,[])}catch(e){var r=e}Reflect.construct(e,[],n)}else{try{n.call()}catch(e){r=e}e.call(n.prototype)}}else{try{throw Error()}catch(e){r=e}(n=e())&&typeof n.catch==`function`&&n.catch(function(){})}}catch(e){if(e&&r&&typeof e.stack==`string`)return[e.stack,r.stack]}return[null,null]}};r.DetermineComponentFrameRoot.displayName=`DetermineComponentFrameRoot`;var i=Object.getOwnPropertyDescriptor(r.DetermineComponentFrameRoot,`name`);i&&i.configurable&&Object.defineProperty(r.DetermineComponentFrameRoot,"name",{value:`DetermineComponentFrameRoot`});var a=r.DetermineComponentFrameRoot(),o=a[0],s=a[1];if(o&&s){var c=o.split(`
`),l=s.split(`
`);for(i=r=0;r<c.length&&!c[r].includes(`DetermineComponentFrameRoot`);)r++;for(;i<l.length&&!l[i].includes(`DetermineComponentFrameRoot`);)i++;if(r===c.length||i===l.length)for(r=c.length-1,i=l.length-1;1<=r&&0<=i&&c[r]!==l[i];)i--;for(;1<=r&&0<=i;r--,i--)if(c[r]!==l[i]){if(r!==1||i!==1)do if(r--,i--,0>i||c[r]!==l[i]){var u=`
`+c[r].replace(` at new `,` at `);return e.displayName&&u.includes(`<anonymous>`)&&(u=u.replace(`<anonymous>`,e.displayName)),u}while(1<=r&&0<=i);break}}}finally{le=!1,Error.prepareStackTrace=n}return(n=e?e.displayName||e.name:``)?ce(n):``}function de(e,t){switch(e.tag){case 26:case 27:case 5:return ce(e.type);case 16:return ce(`Lazy`);case 13:return e.child!==t&&t!==null?ce(`Suspense Fallback`):ce(`Suspense`);case 19:return ce(`SuspenseList`);case 0:case 15:return ue(e.type,!1);case 11:return ue(e.type.render,!1);case 1:return ue(e.type,!0);case 31:return ce(`Activity`);default:return``}}function fe(e){try{var t=``,n=null;do t+=de(e,n),n=e,e=e.return;while(e);return t}catch(e){return`
Error generating stack: `+e.message+`
`+e.stack}}var pe=Object.prototype.hasOwnProperty,me=t.unstable_scheduleCallback,he=t.unstable_cancelCallback,ge=t.unstable_shouldYield,_e=t.unstable_requestPaint,ve=t.unstable_now,ye=t.unstable_getCurrentPriorityLevel,K=t.unstable_ImmediatePriority,be=t.unstable_UserBlockingPriority,xe=t.unstable_NormalPriority,q=t.unstable_LowPriority,Se=t.unstable_IdlePriority,Ce=t.log,we=t.unstable_setDisableYieldValue,Te=null,Ee=null;function De(e){if(typeof Ce==`function`&&we(e),Ee&&typeof Ee.setStrictMode==`function`)try{Ee.setStrictMode(Te,e)}catch{}}var Oe=Math.clz32?Math.clz32:je,ke=Math.log,Ae=Math.LN2;function je(e){return e>>>=0,e===0?32:31-(ke(e)/Ae|0)|0}var Me=256,Ne=262144,Pe=4194304;function Fe(e){var t=e&42;if(t!==0)return t;switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:return 64;case 128:return 128;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:return e&261888;case 262144:case 524288:case 1048576:case 2097152:return e&3932160;case 4194304:case 8388608:case 16777216:case 33554432:return e&62914560;case 67108864:return 67108864;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 0;default:return e}}function Ie(e,t,n){var r=e.pendingLanes;if(r===0)return 0;var i=0,a=e.suspendedLanes,o=e.pingedLanes;e=e.warmLanes;var s=r&134217727;return s===0?(s=r&~a,s===0?o===0?n||(n=r&~e,n!==0&&(i=Fe(n))):i=Fe(o):i=Fe(s)):(r=s&~a,r===0?(o&=s,o===0?n||(n=s&~e,n!==0&&(i=Fe(n))):i=Fe(o)):i=Fe(r)),i===0?0:t!==0&&t!==i&&(t&a)===0&&(a=i&-i,n=t&-t,a>=n||a===32&&n&4194048)?t:i}function Le(e,t){return(e.pendingLanes&~(e.suspendedLanes&~e.pingedLanes)&t)===0}function Re(e,t){switch(e){case 1:case 2:case 4:case 8:case 64:return t+250;case 16:case 32:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return t+5e3;case 4194304:case 8388608:case 16777216:case 33554432:return-1;case 67108864:case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function ze(){var e=Pe;return Pe<<=1,!(Pe&62914560)&&(Pe=4194304),e}function Be(e){for(var t=[],n=0;31>n;n++)t.push(e);return t}function Ve(e,t){e.pendingLanes|=t,t!==268435456&&(e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0)}function He(e,t,n,r,i,a){var o=e.pendingLanes;e.pendingLanes=n,e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0,e.expiredLanes&=n,e.entangledLanes&=n,e.errorRecoveryDisabledLanes&=n,e.shellSuspendCounter=0;var s=e.entanglements,c=e.expirationTimes,l=e.hiddenUpdates;for(n=o&~n;0<n;){var u=31-Oe(n),d=1<<u;s[u]=0,c[u]=-1;var f=l[u];if(f!==null)for(l[u]=null,u=0;u<f.length;u++){var p=f[u];p!==null&&(p.lane&=-536870913)}n&=~d}r!==0&&Ue(e,r,0),a!==0&&i===0&&e.tag!==0&&(e.suspendedLanes|=a&~(o&~t))}function Ue(e,t,n){e.pendingLanes|=t,e.suspendedLanes&=~t;var r=31-Oe(t);e.entangledLanes|=t,e.entanglements[r]=e.entanglements[r]|1073741824|n&261930}function We(e,t){var n=e.entangledLanes|=t;for(e=e.entanglements;n;){var r=31-Oe(n),i=1<<r;i&t|e[r]&t&&(e[r]|=t),n&=~i}}function Ge(e,t){var n=t&-t;return n=n&42?1:Ke(n),(n&(e.suspendedLanes|t))===0?n:0}function Ke(e){switch(e){case 2:e=1;break;case 8:e=4;break;case 32:e=16;break;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:e=128;break;case 268435456:e=134217728;break;default:e=0}return e}function qe(e){return e&=-e,2<e?8<e?e&134217727?32:268435456:8:2}function Je(){var e=L.p;return e===0?(e=window.event,e===void 0?32:mp(e.type)):e}function Ye(e,t){var n=L.p;try{return L.p=e,t()}finally{L.p=n}}var Xe=Math.random().toString(36).slice(2),Ze=`__reactFiber$`+Xe,Qe=`__reactProps$`+Xe,$e=`__reactContainer$`+Xe,et=`__reactEvents$`+Xe,tt=`__reactListeners$`+Xe,nt=`__reactHandles$`+Xe,rt=`__reactResources$`+Xe,it=`__reactMarker$`+Xe;function at(e){delete e[Ze],delete e[Qe],delete e[et],delete e[tt],delete e[nt]}function ot(e){var t=e[Ze];if(t)return t;for(var n=e.parentNode;n;){if(t=n[$e]||n[Ze]){if(n=t.alternate,t.child!==null||n!==null&&n.child!==null)for(e=df(e);e!==null;){if(n=e[Ze])return n;e=df(e)}return t}e=n,n=e.parentNode}return null}function st(e){if(e=e[Ze]||e[$e]){var t=e.tag;if(t===5||t===6||t===13||t===31||t===26||t===27||t===3)return e}return null}function ct(e){var t=e.tag;if(t===5||t===26||t===27||t===6)return e.stateNode;throw Error(i(33))}function lt(e){var t=e[rt];return t||=e[rt]={hoistableStyles:new Map,hoistableScripts:new Map},t}function ut(e){e[it]=!0}var dt=new Set,ft={};function pt(e,t){mt(e,t),mt(e+`Capture`,t)}function mt(e,t){for(ft[e]=t,e=0;e<t.length;e++)dt.add(t[e])}var ht=RegExp(`^[:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD][:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD\\-.0-9\\u00B7\\u0300-\\u036F\\u203F-\\u2040]*$`),gt={},_t={};function vt(e){return pe.call(_t,e)?!0:pe.call(gt,e)?!1:ht.test(e)?_t[e]=!0:(gt[e]=!0,!1)}function yt(e,t,n){if(vt(t)){if(n===null)e.removeAttribute(t);else{switch(typeof n){case`undefined`:case`function`:case`symbol`:e.removeAttribute(t);return;case`boolean`:var r=t.toLowerCase().slice(0,5);if(r!==`data-`&&r!==`aria-`){e.removeAttribute(t);return}}e.setAttribute(t,``+n)}}}function bt(e,t,n){if(n===null)e.removeAttribute(t);else{switch(typeof n){case`undefined`:case`function`:case`symbol`:case`boolean`:e.removeAttribute(t);return}e.setAttribute(t,``+n)}}function xt(e,t,n,r){if(r===null)e.removeAttribute(n);else{switch(typeof r){case`undefined`:case`function`:case`symbol`:case`boolean`:e.removeAttribute(n);return}e.setAttributeNS(t,n,``+r)}}function St(e){switch(typeof e){case`bigint`:case`boolean`:case`number`:case`string`:case`undefined`:return e;case`object`:return e;default:return``}}function Ct(e){var t=e.type;return(e=e.nodeName)&&e.toLowerCase()===`input`&&(t===`checkbox`||t===`radio`)}function wt(e,t,n){var r=Object.getOwnPropertyDescriptor(e.constructor.prototype,t);if(!e.hasOwnProperty(t)&&r!==void 0&&typeof r.get==`function`&&typeof r.set==`function`){var i=r.get,a=r.set;return Object.defineProperty(e,t,{configurable:!0,get:function(){return i.call(this)},set:function(e){n=``+e,a.call(this,e)}}),Object.defineProperty(e,t,{enumerable:r.enumerable}),{getValue:function(){return n},setValue:function(e){n=``+e},stopTracking:function(){e._valueTracker=null,delete e[t]}}}}function Tt(e){if(!e._valueTracker){var t=Ct(e)?`checked`:`value`;e._valueTracker=wt(e,t,``+e[t])}}function Et(e){if(!e)return!1;var t=e._valueTracker;if(!t)return!0;var n=t.getValue(),r=``;return e&&(r=Ct(e)?e.checked?`true`:`false`:e.value),e=r,e!==n&&(t.setValue(e),!0)}function Dt(e){if(e||=typeof document<`u`?document:void 0,e===void 0)return null;try{return e.activeElement||e.body}catch{return e.body}}var Ot=/[\n"\\]/g;function kt(e){return e.replace(Ot,function(e){return`\\`+e.charCodeAt(0).toString(16)+` `})}function At(e,t,n,r,i,a,o,s){e.name=``,o!=null&&typeof o!=`function`&&typeof o!=`symbol`&&typeof o!=`boolean`?e.type=o:e.removeAttribute(`type`),t==null?o!==`submit`&&o!==`reset`||e.removeAttribute(`value`):o===`number`?(t===0&&e.value===``||e.value!=t)&&(e.value=``+St(t)):e.value!==``+St(t)&&(e.value=``+St(t)),t==null?n==null?r!=null&&e.removeAttribute(`value`):Mt(e,o,St(n)):Mt(e,o,St(t)),i==null&&a!=null&&(e.defaultChecked=!!a),i!=null&&(e.checked=i&&typeof i!=`function`&&typeof i!=`symbol`),s!=null&&typeof s!=`function`&&typeof s!=`symbol`&&typeof s!=`boolean`?e.name=``+St(s):e.removeAttribute(`name`)}function jt(e,t,n,r,i,a,o,s){if(a!=null&&typeof a!=`function`&&typeof a!=`symbol`&&typeof a!=`boolean`&&(e.type=a),t!=null||n!=null){if(!(a!==`submit`&&a!==`reset`||t!=null)){Tt(e);return}n=n==null?``:``+St(n),t=t==null?n:``+St(t),s||t===e.value||(e.value=t),e.defaultValue=t}r??=i,r=typeof r!=`function`&&typeof r!=`symbol`&&!!r,e.checked=s?e.checked:!!r,e.defaultChecked=!!r,o!=null&&typeof o!=`function`&&typeof o!=`symbol`&&typeof o!=`boolean`&&(e.name=o),Tt(e)}function Mt(e,t,n){t===`number`&&Dt(e.ownerDocument)===e||e.defaultValue===``+n||(e.defaultValue=``+n)}function Nt(e,t,n,r){if(e=e.options,t){t={};for(var i=0;i<n.length;i++)t[`$`+n[i]]=!0;for(n=0;n<e.length;n++)i=t.hasOwnProperty(`$`+e[n].value),e[n].selected!==i&&(e[n].selected=i),i&&r&&(e[n].defaultSelected=!0)}else{for(n=``+St(n),t=null,i=0;i<e.length;i++){if(e[i].value===n){e[i].selected=!0,r&&(e[i].defaultSelected=!0);return}t!==null||e[i].disabled||(t=e[i])}t!==null&&(t.selected=!0)}}function Pt(e,t,n){if(t!=null&&(t=``+St(t),t!==e.value&&(e.value=t),n==null)){e.defaultValue!==t&&(e.defaultValue=t);return}e.defaultValue=n==null?``:``+St(n)}function Ft(e,t,n,r){if(t==null){if(r!=null){if(n!=null)throw Error(i(92));if(F(r)){if(1<r.length)throw Error(i(93));r=r[0]}n=r}n??=``,t=n}n=St(t),e.defaultValue=n,r=e.textContent,r===n&&r!==``&&r!==null&&(e.value=r),Tt(e)}function It(e,t){if(t){var n=e.firstChild;if(n&&n===e.lastChild&&n.nodeType===3){n.nodeValue=t;return}}e.textContent=t}var Lt=new Set(`animationIterationCount aspectRatio borderImageOutset borderImageSlice borderImageWidth boxFlex boxFlexGroup boxOrdinalGroup columnCount columns flex flexGrow flexPositive flexShrink flexNegative flexOrder gridArea gridRow gridRowEnd gridRowSpan gridRowStart gridColumn gridColumnEnd gridColumnSpan gridColumnStart fontWeight lineClamp lineHeight opacity order orphans scale tabSize widows zIndex zoom fillOpacity floodOpacity stopOpacity strokeDasharray strokeDashoffset strokeMiterlimit strokeOpacity strokeWidth MozAnimationIterationCount MozBoxFlex MozBoxFlexGroup MozLineClamp msAnimationIterationCount msFlex msZoom msFlexGrow msFlexNegative msFlexOrder msFlexPositive msFlexShrink msGridColumn msGridColumnSpan msGridRow msGridRowSpan WebkitAnimationIterationCount WebkitBoxFlex WebKitBoxFlexGroup WebkitBoxOrdinalGroup WebkitColumnCount WebkitColumns WebkitFlex WebkitFlexGrow WebkitFlexPositive WebkitFlexShrink WebkitLineClamp`.split(` `));function Rt(e,t,n){var r=t.indexOf(`--`)===0;n==null||typeof n==`boolean`||n===``?r?e.setProperty(t,``):t===`float`?e.cssFloat=``:e[t]=``:r?e.setProperty(t,n):typeof n!=`number`||n===0||Lt.has(t)?t===`float`?e.cssFloat=n:e[t]=(``+n).trim():e[t]=n+`px`}function zt(e,t,n){if(t!=null&&typeof t!=`object`)throw Error(i(62));if(e=e.style,n!=null){for(var r in n)!n.hasOwnProperty(r)||t!=null&&t.hasOwnProperty(r)||(r.indexOf(`--`)===0?e.setProperty(r,``):r===`float`?e.cssFloat=``:e[r]=``);for(var a in t)r=t[a],t.hasOwnProperty(a)&&n[a]!==r&&Rt(e,a,r)}else for(var o in t)t.hasOwnProperty(o)&&Rt(e,o,t[o])}function Bt(e){if(e.indexOf(`-`)===-1)return!1;switch(e){case`annotation-xml`:case`color-profile`:case`font-face`:case`font-face-src`:case`font-face-uri`:case`font-face-format`:case`font-face-name`:case`missing-glyph`:return!1;default:return!0}}var Vt=new Map([[`acceptCharset`,`accept-charset`],[`htmlFor`,`for`],[`httpEquiv`,`http-equiv`],[`crossOrigin`,`crossorigin`],[`accentHeight`,`accent-height`],[`alignmentBaseline`,`alignment-baseline`],[`arabicForm`,`arabic-form`],[`baselineShift`,`baseline-shift`],[`capHeight`,`cap-height`],[`clipPath`,`clip-path`],[`clipRule`,`clip-rule`],[`colorInterpolation`,`color-interpolation`],[`colorInterpolationFilters`,`color-interpolation-filters`],[`colorProfile`,`color-profile`],[`colorRendering`,`color-rendering`],[`dominantBaseline`,`dominant-baseline`],[`enableBackground`,`enable-background`],[`fillOpacity`,`fill-opacity`],[`fillRule`,`fill-rule`],[`floodColor`,`flood-color`],[`floodOpacity`,`flood-opacity`],[`fontFamily`,`font-family`],[`fontSize`,`font-size`],[`fontSizeAdjust`,`font-size-adjust`],[`fontStretch`,`font-stretch`],[`fontStyle`,`font-style`],[`fontVariant`,`font-variant`],[`fontWeight`,`font-weight`],[`glyphName`,`glyph-name`],[`glyphOrientationHorizontal`,`glyph-orientation-horizontal`],[`glyphOrientationVertical`,`glyph-orientation-vertical`],[`horizAdvX`,`horiz-adv-x`],[`horizOriginX`,`horiz-origin-x`],[`imageRendering`,`image-rendering`],[`letterSpacing`,`letter-spacing`],[`lightingColor`,`lighting-color`],[`markerEnd`,`marker-end`],[`markerMid`,`marker-mid`],[`markerStart`,`marker-start`],[`overlinePosition`,`overline-position`],[`overlineThickness`,`overline-thickness`],[`paintOrder`,`paint-order`],[`panose-1`,`panose-1`],[`pointerEvents`,`pointer-events`],[`renderingIntent`,`rendering-intent`],[`shapeRendering`,`shape-rendering`],[`stopColor`,`stop-color`],[`stopOpacity`,`stop-opacity`],[`strikethroughPosition`,`strikethrough-position`],[`strikethroughThickness`,`strikethrough-thickness`],[`strokeDasharray`,`stroke-dasharray`],[`strokeDashoffset`,`stroke-dashoffset`],[`strokeLinecap`,`stroke-linecap`],[`strokeLinejoin`,`stroke-linejoin`],[`strokeMiterlimit`,`stroke-miterlimit`],[`strokeOpacity`,`stroke-opacity`],[`strokeWidth`,`stroke-width`],[`textAnchor`,`text-anchor`],[`textDecoration`,`text-decoration`],[`textRendering`,`text-rendering`],[`transformOrigin`,`transform-origin`],[`underlinePosition`,`underline-position`],[`underlineThickness`,`underline-thickness`],[`unicodeBidi`,`unicode-bidi`],[`unicodeRange`,`unicode-range`],[`unitsPerEm`,`units-per-em`],[`vAlphabetic`,`v-alphabetic`],[`vHanging`,`v-hanging`],[`vIdeographic`,`v-ideographic`],[`vMathematical`,`v-mathematical`],[`vectorEffect`,`vector-effect`],[`vertAdvY`,`vert-adv-y`],[`vertOriginX`,`vert-origin-x`],[`vertOriginY`,`vert-origin-y`],[`wordSpacing`,`word-spacing`],[`writingMode`,`writing-mode`],[`xmlnsXlink`,`xmlns:xlink`],[`xHeight`,`x-height`]]),Ht=/^[\u0000-\u001F ]*j[\r\n\t]*a[\r\n\t]*v[\r\n\t]*a[\r\n\t]*s[\r\n\t]*c[\r\n\t]*r[\r\n\t]*i[\r\n\t]*p[\r\n\t]*t[\r\n\t]*:/i;function Ut(e){return Ht.test(``+e)?`javascript:throw new Error('React has blocked a javascript: URL as a security precaution.')`:e}function Wt(){}var Gt=null;function Kt(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var qt=null,Jt=null;function Yt(e){var t=st(e);if(t&&(e=t.stateNode)){var n=e[Qe]||null;a:switch(e=t.stateNode,t.type){case`input`:if(At(e,n.value,n.defaultValue,n.defaultValue,n.checked,n.defaultChecked,n.type,n.name),t=n.name,n.type===`radio`&&t!=null){for(n=e;n.parentNode;)n=n.parentNode;for(n=n.querySelectorAll(`input[name="`+kt(``+t)+`"][type="radio"]`),t=0;t<n.length;t++){var r=n[t];if(r!==e&&r.form===e.form){var a=r[Qe]||null;if(!a)throw Error(i(90));At(r,a.value,a.defaultValue,a.defaultValue,a.checked,a.defaultChecked,a.type,a.name)}}for(t=0;t<n.length;t++)r=n[t],r.form===e.form&&Et(r)}break a;case`textarea`:Pt(e,n.value,n.defaultValue);break a;case`select`:t=n.value,t!=null&&Nt(e,!!n.multiple,t,!1)}}}var Xt=!1;function Zt(e,t,n){if(Xt)return e(t,n);Xt=!0;try{return e(t)}finally{if(Xt=!1,(qt!==null||Jt!==null)&&(_u(),qt&&(t=qt,e=Jt,Jt=qt=null,Yt(t),e)))for(t=0;t<e.length;t++)Yt(e[t])}}function Qt(e,t){var n=e.stateNode;if(n===null)return null;var r=n[Qe]||null;if(r===null)return null;n=r[t];a:switch(t){case`onClick`:case`onClickCapture`:case`onDoubleClick`:case`onDoubleClickCapture`:case`onMouseDown`:case`onMouseDownCapture`:case`onMouseMove`:case`onMouseMoveCapture`:case`onMouseUp`:case`onMouseUpCapture`:case`onMouseEnter`:(r=!r.disabled)||(e=e.type,r=e!==`button`&&e!==`input`&&e!==`select`&&e!==`textarea`),e=!r;break a;default:e=!1}if(e)return null;if(n&&typeof n!=`function`)throw Error(i(231,t,typeof n));return n}var $t=!(typeof window>`u`||window.document===void 0||window.document.createElement===void 0),en=!1;if($t)try{var tn={};Object.defineProperty(tn,"passive",{get:function(){en=!0}}),window.addEventListener(`test`,tn,tn),window.removeEventListener(`test`,tn,tn)}catch{en=!1}var nn=null,rn=null,an=null;function on(){if(an)return an;var e,t=rn,n=t.length,r,i=`value`in nn?nn.value:nn.textContent,a=i.length;for(e=0;e<n&&t[e]===i[e];e++);var o=n-e;for(r=1;r<=o&&t[n-r]===i[a-r];r++);return an=i.slice(e,1<r?1-r:void 0)}function sn(e){var t=e.keyCode;return`charCode`in e?(e=e.charCode,e===0&&t===13&&(e=13)):e=t,e===10&&(e=13),32<=e||e===13?e:0}function cn(){return!0}function ln(){return!1}function un(e){function t(t,n,r,i,a){for(var o in this._reactName=t,this._targetInst=r,this.type=n,this.nativeEvent=i,this.target=a,this.currentTarget=null,e)e.hasOwnProperty(o)&&(t=e[o],this[o]=t?t(i):i[o]);return this.isDefaultPrevented=(i.defaultPrevented==null?!1===i.returnValue:i.defaultPrevented)?cn:ln,this.isPropagationStopped=ln,this}return h(t.prototype,{preventDefault:function(){this.defaultPrevented=!0;var e=this.nativeEvent;e&&(e.preventDefault?e.preventDefault():typeof e.returnValue!=`unknown`&&(e.returnValue=!1),this.isDefaultPrevented=cn)},stopPropagation:function(){var e=this.nativeEvent;e&&(e.stopPropagation?e.stopPropagation():typeof e.cancelBubble!=`unknown`&&(e.cancelBubble=!0),this.isPropagationStopped=cn)},persist:function(){},isPersistent:cn}),t}var dn={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},fn=un(dn),pn=h({},dn,{view:0,detail:0}),mn=un(pn),hn,gn,_n,vn=h({},pn,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:On,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return`movementX`in e?e.movementX:(e!==_n&&(_n&&e.type===`mousemove`?(hn=e.screenX-_n.screenX,gn=e.screenY-_n.screenY):gn=hn=0,_n=e),hn)},movementY:function(e){return`movementY`in e?e.movementY:gn}}),yn=un(vn),bn=un(h({},vn,{dataTransfer:0})),xn=un(h({},pn,{relatedTarget:0})),Sn=un(h({},dn,{animationName:0,elapsedTime:0,pseudoElement:0})),Cn=un(h({},dn,{clipboardData:function(e){return`clipboardData`in e?e.clipboardData:window.clipboardData}})),J=un(h({},dn,{data:0})),wn={Esc:`Escape`,Spacebar:` `,Left:`ArrowLeft`,Up:`ArrowUp`,Right:`ArrowRight`,Down:`ArrowDown`,Del:`Delete`,Win:`OS`,Menu:`ContextMenu`,Apps:`ContextMenu`,Scroll:`ScrollLock`,MozPrintableKey:`Unidentified`},Tn={8:`Backspace`,9:`Tab`,12:`Clear`,13:`Enter`,16:`Shift`,17:`Control`,18:`Alt`,19:`Pause`,20:`CapsLock`,27:`Escape`,32:` `,33:`PageUp`,34:`PageDown`,35:`End`,36:`Home`,37:`ArrowLeft`,38:`ArrowUp`,39:`ArrowRight`,40:`ArrowDown`,45:`Insert`,46:`Delete`,112:`F1`,113:`F2`,114:`F3`,115:`F4`,116:`F5`,117:`F6`,118:`F7`,119:`F8`,120:`F9`,121:`F10`,122:`F11`,123:`F12`,144:`NumLock`,145:`ScrollLock`,224:`Meta`},En={Alt:`altKey`,Control:`ctrlKey`,Meta:`metaKey`,Shift:`shiftKey`};function Dn(e){var t=this.nativeEvent;return t.getModifierState?t.getModifierState(e):(e=En[e])?!!t[e]:!1}function On(){return Dn}var kn=un(h({},pn,{key:function(e){if(e.key){var t=wn[e.key]||e.key;if(t!==`Unidentified`)return t}return e.type===`keypress`?(e=sn(e),e===13?`Enter`:String.fromCharCode(e)):e.type===`keydown`||e.type===`keyup`?Tn[e.keyCode]||`Unidentified`:``},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:On,charCode:function(e){return e.type===`keypress`?sn(e):0},keyCode:function(e){return e.type===`keydown`||e.type===`keyup`?e.keyCode:0},which:function(e){return e.type===`keypress`?sn(e):e.type===`keydown`||e.type===`keyup`?e.keyCode:0}})),An=un(h({},vn,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0})),Y=un(h({},pn,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:On})),jn=un(h({},dn,{propertyName:0,elapsedTime:0,pseudoElement:0})),Mn=un(h({},vn,{deltaX:function(e){return`deltaX`in e?e.deltaX:`wheelDeltaX`in e?-e.wheelDeltaX:0},deltaY:function(e){return`deltaY`in e?e.deltaY:`wheelDeltaY`in e?-e.wheelDeltaY:`wheelDelta`in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0})),Nn=un(h({},dn,{newState:0,oldState:0})),Pn=[9,13,27,32],Fn=$t&&`CompositionEvent`in window,In=null;$t&&`documentMode`in document&&(In=document.documentMode);var Ln=$t&&`TextEvent`in window&&!In,Rn=$t&&(!Fn||In&&8<In&&11>=In),zn=` `,Bn=!1;function Vn(e,t){switch(e){case`keyup`:return Pn.indexOf(t.keyCode)!==-1;case`keydown`:return t.keyCode!==229;case`keypress`:case`mousedown`:case`focusout`:return!0;default:return!1}}function Hn(e){return e=e.detail,typeof e==`object`&&`data`in e?e.data:null}var Un=!1;function Wn(e,t){switch(e){case`compositionend`:return Hn(t);case`keypress`:return t.which===32?(Bn=!0,zn):null;case`textInput`:return e=t.data,e===zn&&Bn?null:e;default:return null}}function Gn(e,t){if(Un)return e===`compositionend`||!Fn&&Vn(e,t)?(e=on(),an=rn=nn=null,Un=!1,e):null;switch(e){case`paste`:return null;case`keypress`:if(!(t.ctrlKey||t.altKey||t.metaKey)||t.ctrlKey&&t.altKey){if(t.char&&1<t.char.length)return t.char;if(t.which)return String.fromCharCode(t.which)}return null;case`compositionend`:return Rn&&t.locale!==`ko`?null:t.data;default:return null}}var Kn={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function qn(e){var t=e&&e.nodeName&&e.nodeName.toLowerCase();return t===`input`?!!Kn[e.type]:t===`textarea`}function Jn(e,t,n,r){qt?Jt?Jt.push(r):Jt=[r]:qt=r,t=Td(t,`onChange`),0<t.length&&(n=new fn(`onChange`,`change`,null,n,r),e.push({event:n,listeners:t}))}var X=null,Yn=null;function Xn(e){_d(e,0)}function Z(e){if(Et(ct(e)))return e}function Zn(e,t){if(e===`change`)return t}var Qn=!1;if($t){var $n;if($t){var er=`oninput`in document;if(!er){var tr=document.createElement(`div`);tr.setAttribute(`oninput`,`return;`),er=typeof tr.oninput==`function`}$n=er}else $n=!1;Qn=$n&&(!document.documentMode||9<document.documentMode)}function nr(){X&&(X.detachEvent(`onpropertychange`,rr),Yn=X=null)}function rr(e){if(e.propertyName===`value`&&Z(Yn)){var t=[];Jn(t,Yn,e,Kt(e)),Zt(Xn,t)}}function ir(e,t,n){e===`focusin`?(nr(),X=t,Yn=n,X.attachEvent(`onpropertychange`,rr)):e===`focusout`&&nr()}function ar(e){if(e===`selectionchange`||e===`keyup`||e===`keydown`)return Z(Yn)}function or(e,t){if(e===`click`)return Z(t)}function sr(e,t){if(e===`input`||e===`change`)return Z(t)}function cr(e,t){return e===t&&(e!==0||1/e==1/t)||e!==e&&t!==t}var lr=typeof Object.is==`function`?Object.is:cr;function ur(e,t){if(lr(e,t))return!0;if(typeof e!=`object`||!e||typeof t!=`object`||!t)return!1;var n=Object.keys(e),r=Object.keys(t);if(n.length!==r.length)return!1;for(r=0;r<n.length;r++){var i=n[r];if(!pe.call(t,i)||!lr(e[i],t[i]))return!1}return!0}function dr(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function fr(e,t){var n=dr(e);e=0;for(var r;n;){if(n.nodeType===3){if(r=e+n.textContent.length,e<=t&&r>=t)return{node:n,offset:t-e};e=r}a:{for(;n;){if(n.nextSibling){n=n.nextSibling;break a}n=n.parentNode}n=void 0}n=dr(n)}}function pr(e,t){return e&&t?e===t?!0:e&&e.nodeType===3?!1:t&&t.nodeType===3?pr(e,t.parentNode):`contains`in e?e.contains(t):e.compareDocumentPosition?!!(e.compareDocumentPosition(t)&16):!1:!1}function mr(e){e=e!=null&&e.ownerDocument!=null&&e.ownerDocument.defaultView!=null?e.ownerDocument.defaultView:window;for(var t=Dt(e.document);t instanceof e.HTMLIFrameElement;){try{var n=typeof t.contentWindow.location.href==`string`}catch{n=!1}if(n)e=t.contentWindow;else break;t=Dt(e.document)}return t}function hr(e){var t=e&&e.nodeName&&e.nodeName.toLowerCase();return t&&(t===`input`&&(e.type===`text`||e.type===`search`||e.type===`tel`||e.type===`url`||e.type===`password`)||t===`textarea`||e.contentEditable===`true`)}var gr=$t&&`documentMode`in document&&11>=document.documentMode,_r=null,vr=null,yr=null,br=!1;function xr(e,t,n){var r=n.window===n?n.document:n.nodeType===9?n:n.ownerDocument;br||_r==null||_r!==Dt(r)||(r=_r,`selectionStart`in r&&hr(r)?r={start:r.selectionStart,end:r.selectionEnd}:(r=(r.ownerDocument&&r.ownerDocument.defaultView||window).getSelection(),r={anchorNode:r.anchorNode,anchorOffset:r.anchorOffset,focusNode:r.focusNode,focusOffset:r.focusOffset}),yr&&ur(yr,r)||(yr=r,r=Td(vr,`onSelect`),0<r.length&&(t=new fn(`onSelect`,`select`,null,t,n),e.push({event:t,listeners:r}),t.target=_r)))}function Sr(e,t){var n={};return n[e.toLowerCase()]=t.toLowerCase(),n[`Webkit`+e]=`webkit`+t,n[`Moz`+e]=`moz`+t,n}var Cr={animationend:Sr(`Animation`,`AnimationEnd`),animationiteration:Sr(`Animation`,`AnimationIteration`),animationstart:Sr(`Animation`,`AnimationStart`),transitionrun:Sr(`Transition`,`TransitionRun`),transitionstart:Sr(`Transition`,`TransitionStart`),transitioncancel:Sr(`Transition`,`TransitionCancel`),transitionend:Sr(`Transition`,`TransitionEnd`)},wr={},Tr={};$t&&(Tr=document.createElement(`div`).style,`AnimationEvent`in window||(delete Cr.animationend.animation,delete Cr.animationiteration.animation,delete Cr.animationstart.animation),`TransitionEvent`in window||delete Cr.transitionend.transition);function Er(e){if(wr[e])return wr[e];if(!Cr[e])return e;var t=Cr[e],n;for(n in t)if(t.hasOwnProperty(n)&&n in Tr)return wr[e]=t[n];return e}var Dr=Er(`animationend`),Or=Er(`animationiteration`),kr=Er(`animationstart`),Ar=Er(`transitionrun`),jr=Er(`transitionstart`),Mr=Er(`transitioncancel`),Nr=Er(`transitionend`),Pr=new Map,Fr=`abort auxClick beforeToggle cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel`.split(` `);Fr.push(`scrollEnd`);function Ir(e,t){Pr.set(e,t),pt(t,[e])}var Lr=typeof reportError==`function`?reportError:function(e){if(typeof window==`object`&&typeof window.ErrorEvent==`function`){var t=new window.ErrorEvent(`error`,{bubbles:!0,cancelable:!0,message:typeof e==`object`&&e&&typeof e.message==`string`?String(e.message):String(e),error:e});if(!window.dispatchEvent(t))return}else if(typeof process==`object`&&typeof process.emit==`function`){process.emit(`uncaughtException`,e);return}console.error(e)},Rr=[],zr=0,Br=0;function Vr(){for(var e=zr,t=Br=zr=0;t<e;){var n=Rr[t];Rr[t++]=null;var r=Rr[t];Rr[t++]=null;var i=Rr[t];Rr[t++]=null;var a=Rr[t];if(Rr[t++]=null,r!==null&&i!==null){var o=r.pending;o===null?i.next=i:(i.next=o.next,o.next=i),r.pending=i}a!==0&&Gr(n,i,a)}}function Hr(e,t,n,r){Rr[zr++]=e,Rr[zr++]=t,Rr[zr++]=n,Rr[zr++]=r,Br|=r,e.lanes|=r,e=e.alternate,e!==null&&(e.lanes|=r)}function Ur(e,t,n,r){return Hr(e,t,n,r),Kr(e)}function Wr(e,t){return Hr(e,null,null,t),Kr(e)}function Gr(e,t,n){e.lanes|=n;var r=e.alternate;r!==null&&(r.lanes|=n);for(var i=!1,a=e.return;a!==null;)a.childLanes|=n,r=a.alternate,r!==null&&(r.childLanes|=n),a.tag===22&&(e=a.stateNode,e===null||e._visibility&1||(i=!0)),e=a,a=a.return;return e.tag===3?(a=e.stateNode,i&&t!==null&&(i=31-Oe(n),e=a.hiddenUpdates,r=e[i],r===null?e[i]=[t]:r.push(t),t.lane=n|536870912),a):null}function Kr(e){if(50<cu)throw cu=0,lu=null,Error(i(185));for(var t=e.return;t!==null;)e=t,t=e.return;return e.tag===3?e.stateNode:null}var qr={};function Jr(e,t,n,r){this.tag=e,this.key=n,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.refCleanup=this.ref=null,this.pendingProps=t,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=r,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function Yr(e,t,n,r){return new Jr(e,t,n,r)}function Xr(e){return e=e.prototype,!(!e||!e.isReactComponent)}function Zr(e,t){var n=e.alternate;return n===null?(n=Yr(e.tag,t,e.key,e.mode),n.elementType=e.elementType,n.type=e.type,n.stateNode=e.stateNode,n.alternate=e,e.alternate=n):(n.pendingProps=t,n.type=e.type,n.flags=0,n.subtreeFlags=0,n.deletions=null),n.flags=e.flags&65011712,n.childLanes=e.childLanes,n.lanes=e.lanes,n.child=e.child,n.memoizedProps=e.memoizedProps,n.memoizedState=e.memoizedState,n.updateQueue=e.updateQueue,t=e.dependencies,n.dependencies=t===null?null:{lanes:t.lanes,firstContext:t.firstContext},n.sibling=e.sibling,n.index=e.index,n.ref=e.ref,n.refCleanup=e.refCleanup,n}function Qr(e,t){e.flags&=65011714;var n=e.alternate;return n===null?(e.childLanes=0,e.lanes=t,e.child=null,e.subtreeFlags=0,e.memoizedProps=null,e.memoizedState=null,e.updateQueue=null,e.dependencies=null,e.stateNode=null):(e.childLanes=n.childLanes,e.lanes=n.lanes,e.child=n.child,e.subtreeFlags=0,e.deletions=null,e.memoizedProps=n.memoizedProps,e.memoizedState=n.memoizedState,e.updateQueue=n.updateQueue,e.type=n.type,t=n.dependencies,e.dependencies=t===null?null:{lanes:t.lanes,firstContext:t.firstContext}),e}function $r(e,t,n,r,a,o){var s=0;if(r=e,typeof e==`function`)Xr(e)&&(s=1);else if(typeof e==`string`)s=Uf(e,n,W.current)?26:e===`html`||e===`head`||e===`body`?27:5;else a:switch(e){case k:return e=Yr(31,n,t,a),e.elementType=k,e.lanes=o,e;case y:return ei(n.children,a,o,t);case b:s=8,a|=24;break;case x:return e=Yr(12,n,t,a|2),e.elementType=x,e.lanes=o,e;case T:return e=Yr(13,n,t,a),e.elementType=T,e.lanes=o,e;case E:return e=Yr(19,n,t,a),e.elementType=E,e.lanes=o,e;default:if(typeof e==`object`&&e)switch(e.$$typeof){case C:s=10;break a;case S:s=9;break a;case w:s=11;break a;case D:s=14;break a;case O:s=16,r=null;break a}s=29,n=Error(i(130,e===null?`null`:typeof e,``)),r=null}return t=Yr(s,n,t,a),t.elementType=e,t.type=r,t.lanes=o,t}function ei(e,t,n,r){return e=Yr(7,e,r,t),e.lanes=n,e}function ti(e,t,n){return e=Yr(6,e,null,t),e.lanes=n,e}function ni(e){var t=Yr(18,null,null,0);return t.stateNode=e,t}function Q(e,t,n){return t=Yr(4,e.children===null?[]:e.children,e.key,t),t.lanes=n,t.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},t}var ri=new WeakMap;function ii(e,t){if(typeof e==`object`&&e){var n=ri.get(e);return n===void 0?(t={value:e,source:t,stack:fe(t)},ri.set(e,t),t):n}return{value:e,source:t,stack:fe(t)}}var ai=[],oi=0,si=null,ci=0,li=[],ui=0,di=null,fi=1,pi=``;function mi(e,t){ai[oi++]=ci,ai[oi++]=si,si=e,ci=t}function hi(e,t,n){li[ui++]=fi,li[ui++]=pi,li[ui++]=di,di=e;var r=fi;e=pi;var i=32-Oe(r)-1;r&=~(1<<i),n+=1;var a=32-Oe(t)+i;if(30<a){var o=i-i%5;a=(r&(1<<o)-1).toString(32),r>>=o,i-=o,fi=1<<32-Oe(t)+i|n<<i|r,pi=a+e}else fi=1<<a|n<<i|r,pi=e}function gi(e){e.return!==null&&(mi(e,1),hi(e,1,0))}function _i(e){for(;e===si;)si=ai[--oi],ai[oi]=null,ci=ai[--oi],ai[oi]=null;for(;e===di;)di=li[--ui],li[ui]=null,pi=li[--ui],li[ui]=null,fi=li[--ui],li[ui]=null}function vi(e,t){li[ui++]=fi,li[ui++]=pi,li[ui++]=di,fi=t.id,pi=t.overflow,di=e}var yi=null,bi=null,xi=!1,Si=null,Ci=!1,wi=Error(i(519));function Ti(e){throw ji(ii(Error(i(418,1<arguments.length&&arguments[1]!==void 0&&arguments[1]?`text`:`HTML`,``)),e)),wi}function Ei(e){var t=e.stateNode,n=e.type,r=e.memoizedProps;switch(t[Ze]=e,t[Qe]=r,n){case`dialog`:vd(`cancel`,t),vd(`close`,t);break;case`iframe`:case`object`:case`embed`:vd(`load`,t);break;case`video`:case`audio`:for(n=0;n<hd.length;n++)vd(hd[n],t);break;case`source`:vd(`error`,t);break;case`img`:case`image`:case`link`:vd(`error`,t),vd(`load`,t);break;case`details`:vd(`toggle`,t);break;case`input`:vd(`invalid`,t),jt(t,r.value,r.defaultValue,r.checked,r.defaultChecked,r.type,r.name,!0);break;case`select`:vd(`invalid`,t);break;case`textarea`:vd(`invalid`,t),Ft(t,r.value,r.defaultValue,r.children)}n=r.children,typeof n!=`string`&&typeof n!=`number`&&typeof n!=`bigint`||t.textContent===``+n||!0===r.suppressHydrationWarning||jd(t.textContent,n)?(r.popover!=null&&(vd(`beforetoggle`,t),vd(`toggle`,t)),r.onScroll!=null&&vd(`scroll`,t),r.onScrollEnd!=null&&vd(`scrollend`,t),r.onClick!=null&&(t.onclick=Wt),t=!0):t=!1,t||Ti(e,!0)}function Di(e){for(yi=e.return;yi;)switch(yi.tag){case 5:case 31:case 13:Ci=!1;return;case 27:case 3:Ci=!0;return;default:yi=yi.return}}function Oi(e){if(e!==yi)return!1;if(!xi)return Di(e),xi=!0,!1;var t=e.tag,n;if((n=t!==3&&t!==27)&&((n=t===5)&&(n=e.type,n=n===`form`||n===`button`||Ud(e.type,e.memoizedProps)),n=!n),n&&bi&&Ti(e),Di(e),t===13){if(e=e.memoizedState,e=e===null?null:e.dehydrated,!e)throw Error(i(317));bi=uf(e)}else if(t===31){if(e=e.memoizedState,e=e===null?null:e.dehydrated,!e)throw Error(i(317));bi=uf(e)}else t===27?(t=bi,Zd(e.type)?(e=lf,lf=null,bi=e):bi=t):bi=yi?cf(e.stateNode.nextSibling):null;return!0}function ki(){bi=yi=null,xi=!1}function Ai(){var e=Si;return e!==null&&(Jl===null?Jl=e:Jl.push.apply(Jl,e),Si=null),e}function ji(e){Si===null?Si=[e]:Si.push(e)}var Mi=V(null),Ni=null,Pi=null;function Fi(e,t,n){U(Mi,t._currentValue),t._currentValue=n}function Ii(e){e._currentValue=Mi.current,H(Mi)}function Li(e,t,n){for(;e!==null;){var r=e.alternate;if((e.childLanes&t)===t?r!==null&&(r.childLanes&t)!==t&&(r.childLanes|=t):(e.childLanes|=t,r!==null&&(r.childLanes|=t)),e===n)break;e=e.return}}function Ri(e,t,n,r){var a=e.child;for(a!==null&&(a.return=e);a!==null;){var o=a.dependencies;if(o!==null){var s=a.child;o=o.firstContext;a:for(;o!==null;){var c=o;o=a;for(var l=0;l<t.length;l++)if(c.context===t[l]){o.lanes|=n,c=o.alternate,c!==null&&(c.lanes|=n),Li(o.return,n,e),r||(s=null);break a}o=c.next}}else if(a.tag===18){if(s=a.return,s===null)throw Error(i(341));s.lanes|=n,o=s.alternate,o!==null&&(o.lanes|=n),Li(s,n,e),s=null}else s=a.child;if(s!==null)s.return=a;else for(s=a;s!==null;){if(s===e){s=null;break}if(a=s.sibling,a!==null){a.return=s.return,s=a;break}s=s.return}a=s}}function zi(e,t,n,r){e=null;for(var a=t,o=!1;a!==null;){if(!o){if(a.flags&524288)o=!0;else if(a.flags&262144)break}if(a.tag===10){var s=a.alternate;if(s===null)throw Error(i(387));if(s=s.memoizedProps,s!==null){var c=a.type;lr(a.pendingProps.value,s.value)||(e===null?e=[c]:e.push(c))}}else if(a===G.current){if(s=a.alternate,s===null)throw Error(i(387));s.memoizedState.memoizedState!==a.memoizedState.memoizedState&&(e===null?e=[Qf]:e.push(Qf))}a=a.return}e!==null&&Ri(t,e,n,r),t.flags|=262144}function Bi(e){for(e=e.firstContext;e!==null;){if(!lr(e.context._currentValue,e.memoizedValue))return!0;e=e.next}return!1}function Vi(e){Ni=e,Pi=null,e=e.dependencies,e!==null&&(e.firstContext=null)}function Hi(e){return Wi(Ni,e)}function Ui(e,t){return Ni===null&&Vi(e),Wi(e,t)}function Wi(e,t){var n=t._currentValue;if(t={context:t,memoizedValue:n,next:null},Pi===null){if(e===null)throw Error(i(308));Pi=t,e.dependencies={lanes:0,firstContext:t},e.flags|=524288}else Pi=Pi.next=t;return n}var Gi=typeof AbortController<`u`?AbortController:function(){var e=[],t=this.signal={aborted:!1,addEventListener:function(t,n){e.push(n)}};this.abort=function(){t.aborted=!0,e.forEach(function(e){return e()})}},Ki=t.unstable_scheduleCallback,qi=t.unstable_NormalPriority,Ji={$$typeof:C,Consumer:null,Provider:null,_currentValue:null,_currentValue2:null,_threadCount:0};function Yi(){return{controller:new Gi,data:new Map,refCount:0}}function Xi(e){e.refCount--,e.refCount===0&&Ki(qi,function(){e.controller.abort()})}var Zi=null,Qi=0,$i=0,ea=null;function ta(e,t){if(Zi===null){var n=Zi=[];Qi=0,$i=ld(),ea={status:`pending`,value:void 0,then:function(e){n.push(e)}}}return Qi++,t.then(na,na),t}function na(){if(--Qi===0&&Zi!==null){ea!==null&&(ea.status=`fulfilled`);var e=Zi;Zi=null,$i=0,ea=null;for(var t=0;t<e.length;t++)(0,e[t])()}}function ra(e,t){var n=[],r={status:`pending`,value:null,reason:null,then:function(e){n.push(e)}};return e.then(function(){r.status=`fulfilled`,r.value=t;for(var e=0;e<n.length;e++)(0,n[e])(t)},function(e){for(r.status=`rejected`,r.reason=e,e=0;e<n.length;e++)(0,n[e])(void 0)}),r}var ia=I.S;I.S=function(e,t){Zl=ve(),typeof t==`object`&&t&&typeof t.then==`function`&&ta(e,t),ia!==null&&ia(e,t)};var aa=V(null);function oa(){var e=aa.current;return e===null?Ml.pooledCache:e}function sa(e,t){t===null?U(aa,aa.current):U(aa,t.pool)}function ca(){var e=oa();return e===null?null:{parent:Ji._currentValue,pool:e}}var la=Error(i(460)),ua=Error(i(474)),da=Error(i(542)),fa={then:function(){}};function pa(e){return e=e.status,e===`fulfilled`||e===`rejected`}function ma(e,t,n){switch(n=e[n],n===void 0?e.push(t):n!==t&&(t.then(Wt,Wt),t=n),t.status){case`fulfilled`:return t.value;case`rejected`:throw e=t.reason,va(e),e;default:if(typeof t.status==`string`)t.then(Wt,Wt);else{if(e=Ml,e!==null&&100<e.shellSuspendCounter)throw Error(i(482));e=t,e.status=`pending`,e.then(function(e){if(t.status===`pending`){var n=t;n.status=`fulfilled`,n.value=e}},function(e){if(t.status===`pending`){var n=t;n.status=`rejected`,n.reason=e}})}switch(t.status){case`fulfilled`:return t.value;case`rejected`:throw e=t.reason,va(e),e}throw ga=t,la}}function ha(e){try{var t=e._init;return t(e._payload)}catch(e){throw typeof e==`object`&&e&&typeof e.then==`function`?(ga=e,la):e}}var ga=null;function _a(){if(ga===null)throw Error(i(459));var e=ga;return ga=null,e}function va(e){if(e===la||e===da)throw Error(i(483))}var ya=null,ba=0;function xa(e){var t=ba;return ba+=1,ya===null&&(ya=[]),ma(ya,e,t)}function Sa(e,t){t=t.props.ref,e.ref=t===void 0?null:t}function Ca(e,t){throw t.$$typeof===g?Error(i(525)):(e=Object.prototype.toString.call(t),Error(i(31,e===`[object Object]`?`object with keys {`+Object.keys(t).join(`, `)+`}`:e)))}function wa(e){function t(t,n){if(e){var r=t.deletions;r===null?(t.deletions=[n],t.flags|=16):r.push(n)}}function n(n,r){if(!e)return null;for(;r!==null;)t(n,r),r=r.sibling;return null}function r(e){for(var t=new Map;e!==null;)e.key===null?t.set(e.index,e):t.set(e.key,e),e=e.sibling;return t}function a(e,t){return e=Zr(e,t),e.index=0,e.sibling=null,e}function o(t,n,r){return t.index=r,e?(r=t.alternate,r===null?(t.flags|=67108866,n):(r=r.index,r<n?(t.flags|=67108866,n):r)):(t.flags|=1048576,n)}function s(t){return e&&t.alternate===null&&(t.flags|=67108866),t}function c(e,t,n,r){return t===null||t.tag!==6?(t=ti(n,e.mode,r),t.return=e,t):(t=a(t,n),t.return=e,t)}function l(e,t,n,r){var i=n.type;return i===y?d(e,t,n.props.children,r,n.key):t!==null&&(t.elementType===i||typeof i==`object`&&i&&i.$$typeof===O&&ha(i)===t.type)?(t=a(t,n.props),Sa(t,n),t.return=e,t):(t=$r(n.type,n.key,n.props,null,e.mode,r),Sa(t,n),t.return=e,t)}function u(e,t,n,r){return t===null||t.tag!==4||t.stateNode.containerInfo!==n.containerInfo||t.stateNode.implementation!==n.implementation?(t=Q(n,e.mode,r),t.return=e,t):(t=a(t,n.children||[]),t.return=e,t)}function d(e,t,n,r,i){return t===null||t.tag!==7?(t=ei(n,e.mode,r,i),t.return=e,t):(t=a(t,n),t.return=e,t)}function f(e,t,n){if(typeof t==`string`&&t!==``||typeof t==`number`||typeof t==`bigint`)return t=ti(``+t,e.mode,n),t.return=e,t;if(typeof t==`object`&&t){switch(t.$$typeof){case _:return n=$r(t.type,t.key,t.props,null,e.mode,n),Sa(n,t),n.return=e,n;case v:return t=Q(t,e.mode,n),t.return=e,t;case O:return t=ha(t),f(e,t,n)}if(F(t)||M(t))return t=ei(t,e.mode,n,null),t.return=e,t;if(typeof t.then==`function`)return f(e,xa(t),n);if(t.$$typeof===C)return f(e,Ui(e,t),n);Ca(e,t)}return null}function p(e,t,n,r){var i=t===null?null:t.key;if(typeof n==`string`&&n!==``||typeof n==`number`||typeof n==`bigint`)return i===null?c(e,t,``+n,r):null;if(typeof n==`object`&&n){switch(n.$$typeof){case _:return n.key===i?l(e,t,n,r):null;case v:return n.key===i?u(e,t,n,r):null;case O:return n=ha(n),p(e,t,n,r)}if(F(n)||M(n))return i===null?d(e,t,n,r,null):null;if(typeof n.then==`function`)return p(e,t,xa(n),r);if(n.$$typeof===C)return p(e,t,Ui(e,n),r);Ca(e,n)}return null}function m(e,t,n,r,i){if(typeof r==`string`&&r!==``||typeof r==`number`||typeof r==`bigint`)return e=e.get(n)||null,c(t,e,``+r,i);if(typeof r==`object`&&r){switch(r.$$typeof){case _:return e=e.get(r.key===null?n:r.key)||null,l(t,e,r,i);case v:return e=e.get(r.key===null?n:r.key)||null,u(t,e,r,i);case O:return r=ha(r),m(e,t,n,r,i)}if(F(r)||M(r))return e=e.get(n)||null,d(t,e,r,i,null);if(typeof r.then==`function`)return m(e,t,n,xa(r),i);if(r.$$typeof===C)return m(e,t,n,Ui(t,r),i);Ca(t,r)}return null}function h(i,a,s,c){for(var l=null,u=null,d=a,h=a=0,g=null;d!==null&&h<s.length;h++){d.index>h?(g=d,d=null):g=d.sibling;var _=p(i,d,s[h],c);if(_===null){d===null&&(d=g);break}e&&d&&_.alternate===null&&t(i,d),a=o(_,a,h),u===null?l=_:u.sibling=_,u=_,d=g}if(h===s.length)return n(i,d),xi&&mi(i,h),l;if(d===null){for(;h<s.length;h++)d=f(i,s[h],c),d!==null&&(a=o(d,a,h),u===null?l=d:u.sibling=d,u=d);return xi&&mi(i,h),l}for(d=r(d);h<s.length;h++)g=m(d,i,h,s[h],c),g!==null&&(e&&g.alternate!==null&&d.delete(g.key===null?h:g.key),a=o(g,a,h),u===null?l=g:u.sibling=g,u=g);return e&&d.forEach(function(e){return t(i,e)}),xi&&mi(i,h),l}function g(a,s,c,l){if(c==null)throw Error(i(151));for(var u=null,d=null,h=s,g=s=0,_=null,v=c.next();h!==null&&!v.done;g++,v=c.next()){h.index>g?(_=h,h=null):_=h.sibling;var y=p(a,h,v.value,l);if(y===null){h===null&&(h=_);break}e&&h&&y.alternate===null&&t(a,h),s=o(y,s,g),d===null?u=y:d.sibling=y,d=y,h=_}if(v.done)return n(a,h),xi&&mi(a,g),u;if(h===null){for(;!v.done;g++,v=c.next())v=f(a,v.value,l),v!==null&&(s=o(v,s,g),d===null?u=v:d.sibling=v,d=v);return xi&&mi(a,g),u}for(h=r(h);!v.done;g++,v=c.next())v=m(h,a,g,v.value,l),v!==null&&(e&&v.alternate!==null&&h.delete(v.key===null?g:v.key),s=o(v,s,g),d===null?u=v:d.sibling=v,d=v);return e&&h.forEach(function(e){return t(a,e)}),xi&&mi(a,g),u}function b(e,r,o,c){if(typeof o==`object`&&o&&o.type===y&&o.key===null&&(o=o.props.children),typeof o==`object`&&o){switch(o.$$typeof){case _:a:{for(var l=o.key;r!==null;){if(r.key===l){if(l=o.type,l===y){if(r.tag===7){n(e,r.sibling),c=a(r,o.props.children),c.return=e,e=c;break a}}else if(r.elementType===l||typeof l==`object`&&l&&l.$$typeof===O&&ha(l)===r.type){n(e,r.sibling),c=a(r,o.props),Sa(c,o),c.return=e,e=c;break a}n(e,r);break}t(e,r),r=r.sibling}o.type===y?(c=ei(o.props.children,e.mode,c,o.key),c.return=e,e=c):(c=$r(o.type,o.key,o.props,null,e.mode,c),Sa(c,o),c.return=e,e=c)}return s(e);case v:a:{for(l=o.key;r!==null;){if(r.key===l){if(r.tag===4&&r.stateNode.containerInfo===o.containerInfo&&r.stateNode.implementation===o.implementation){n(e,r.sibling),c=a(r,o.children||[]),c.return=e,e=c;break a}n(e,r);break}t(e,r),r=r.sibling}c=Q(o,e.mode,c),c.return=e,e=c}return s(e);case O:return o=ha(o),b(e,r,o,c)}if(F(o))return h(e,r,o,c);if(M(o)){if(l=M(o),typeof l!=`function`)throw Error(i(150));return o=l.call(o),g(e,r,o,c)}if(typeof o.then==`function`)return b(e,r,xa(o),c);if(o.$$typeof===C)return b(e,r,Ui(e,o),c);Ca(e,o)}return typeof o==`string`&&o!==``||typeof o==`number`||typeof o==`bigint`?(o=``+o,r!==null&&r.tag===6?(n(e,r.sibling),c=a(r,o),c.return=e,e=c):(n(e,r),c=ti(o,e.mode,c),c.return=e,e=c),s(e)):n(e,r)}return function(e,t,n,r){try{ba=0;var i=b(e,t,n,r);return ya=null,i}catch(t){if(t===la||t===da)throw t;var a=Yr(29,t,null,e.mode);return a.lanes=r,a.return=e,a}}}var Ta=wa(!0),Ea=wa(!1),Da=!1;function Oa(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,lanes:0,hiddenCallbacks:null},callbacks:null}}function ka(e,t){e=e.updateQueue,t.updateQueue===e&&(t.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,callbacks:null})}function Aa(e){return{lane:e,tag:0,payload:null,callback:null,next:null}}function ja(e,t,n){var r=e.updateQueue;if(r===null)return null;if(r=r.shared,jl&2){var i=r.pending;return i===null?t.next=t:(t.next=i.next,i.next=t),r.pending=t,t=Kr(e),Gr(e,null,n),t}return Hr(e,r,t,n),Kr(e)}function Ma(e,t,n){if(t=t.updateQueue,t!==null&&(t=t.shared,n&4194048)){var r=t.lanes;r&=e.pendingLanes,n|=r,t.lanes=n,We(e,n)}}function Na(e,t){var n=e.updateQueue,r=e.alternate;if(r!==null&&(r=r.updateQueue,n===r)){var i=null,a=null;if(n=n.firstBaseUpdate,n!==null){do{var o={lane:n.lane,tag:n.tag,payload:n.payload,callback:null,next:null};a===null?i=a=o:a=a.next=o,n=n.next}while(n!==null);a===null?i=a=t:a=a.next=t}else i=a=t;n={baseState:r.baseState,firstBaseUpdate:i,lastBaseUpdate:a,shared:r.shared,callbacks:r.callbacks},e.updateQueue=n;return}e=n.lastBaseUpdate,e===null?n.firstBaseUpdate=t:e.next=t,n.lastBaseUpdate=t}var Pa=!1;function Fa(){if(Pa){var e=ea;if(e!==null)throw e}}function Ia(e,t,n,r){Pa=!1;var i=e.updateQueue;Da=!1;var a=i.firstBaseUpdate,o=i.lastBaseUpdate,s=i.shared.pending;if(s!==null){i.shared.pending=null;var c=s,l=c.next;c.next=null,o===null?a=l:o.next=l,o=c;var u=e.alternate;u!==null&&(u=u.updateQueue,s=u.lastBaseUpdate,s!==o&&(s===null?u.firstBaseUpdate=l:s.next=l,u.lastBaseUpdate=c))}if(a!==null){var d=i.baseState;o=0,u=l=c=null,s=a;do{var f=s.lane&-536870913,p=f!==s.lane;if(p?(Pl&f)===f:(r&f)===f){f!==0&&f===$i&&(Pa=!0),u!==null&&(u=u.next={lane:0,tag:s.tag,payload:s.payload,callback:null,next:null});a:{var m=e,g=s;f=t;var _=n;switch(g.tag){case 1:if(m=g.payload,typeof m==`function`){d=m.call(_,d,f);break a}d=m;break a;case 3:m.flags=m.flags&-65537|128;case 0:if(m=g.payload,f=typeof m==`function`?m.call(_,d,f):m,f==null)break a;d=h({},d,f);break a;case 2:Da=!0}}f=s.callback,f!==null&&(e.flags|=64,p&&(e.flags|=8192),p=i.callbacks,p===null?i.callbacks=[f]:p.push(f))}else p={lane:f,tag:s.tag,payload:s.payload,callback:s.callback,next:null},u===null?(l=u=p,c=d):u=u.next=p,o|=f;if(s=s.next,s===null){if(s=i.shared.pending,s===null)break;p=s,s=p.next,p.next=null,i.lastBaseUpdate=p,i.shared.pending=null}}while(1);u===null&&(c=d),i.baseState=c,i.firstBaseUpdate=l,i.lastBaseUpdate=u,a===null&&(i.shared.lanes=0),Hl|=o,e.lanes=o,e.memoizedState=d}}function La(e,t){if(typeof e!=`function`)throw Error(i(191,e));e.call(t)}function Ra(e,t){var n=e.callbacks;if(n!==null)for(e.callbacks=null,e=0;e<n.length;e++)La(n[e],t)}var za=V(null),Ba=V(0);function Va(e,t){e=Bl,U(Ba,e),U(za,t),Bl=e|t.baseLanes}function Ha(){U(Ba,Bl),U(za,za.current)}function Ua(){Bl=Ba.current,H(za),H(Ba)}var Wa=V(null),Ga=null;function Ka(e){var t=e.alternate;U(Za,Za.current&1),U(Wa,e),Ga===null&&(t===null||za.current!==null||t.memoizedState!==null)&&(Ga=e)}function qa(e){U(Za,Za.current),U(Wa,e),Ga===null&&(Ga=e)}function Ja(e){e.tag===22?(U(Za,Za.current),U(Wa,e),Ga===null&&(Ga=e)):Ya(e)}function Ya(){U(Za,Za.current),U(Wa,Wa.current)}function Xa(e){H(Wa),Ga===e&&(Ga=null),H(Za)}var Za=V(0);function Qa(e){for(var t=e;t!==null;){if(t.tag===13){var n=t.memoizedState;if(n!==null&&(n=n.dehydrated,n===null||af(n)||of(n)))return t}else if(t.tag===19&&(t.memoizedProps.revealOrder===`forwards`||t.memoizedProps.revealOrder===`backwards`||t.memoizedProps.revealOrder===`unstable_legacy-backwards`||t.memoizedProps.revealOrder===`together`)){if(t.flags&128)return t}else if(t.child!==null){t.child.return=t,t=t.child;continue}if(t===e)break;for(;t.sibling===null;){if(t.return===null||t.return===e)return null;t=t.return}t.sibling.return=t.return,t=t.sibling}return null}var $a=0,eo=null,to=null,no=null,ro=!1,io=!1,ao=!1,oo=0,so=0,co=null,lo=0;function $(){throw Error(i(321))}function uo(e,t){if(t===null)return!1;for(var n=0;n<t.length&&n<e.length;n++)if(!lr(e[n],t[n]))return!1;return!0}function fo(e,t,n,r,i,a){return $a=a,eo=t,t.memoizedState=null,t.updateQueue=null,t.lanes=0,I.H=e===null||e.memoizedState===null?ks:As,ao=!1,a=n(r,i),ao=!1,io&&(a=mo(t,n,r,i)),po(e),a}function po(e){I.H=Os;var t=to!==null&&to.next!==null;if($a=0,no=to=eo=null,ro=!1,so=0,co=null,t)throw Error(i(300));e===null||qs||(e=e.dependencies,e!==null&&Bi(e)&&(qs=!0))}function mo(e,t,n,r){eo=e;var a=0;do{if(io&&(co=null),so=0,io=!1,25<=a)throw Error(i(301));if(a+=1,no=to=null,e.updateQueue!=null){var o=e.updateQueue;o.lastEffect=null,o.events=null,o.stores=null,o.memoCache!=null&&(o.memoCache.index=0)}I.H=js,o=t(n,r)}while(io);return o}function ho(){var e=I.H,t=e.useState()[0];return t=typeof t.then==`function`?So(t):t,e=e.useState()[0],(to===null?null:to.memoizedState)!==e&&(eo.flags|=1024),t}function go(){var e=oo!==0;return oo=0,e}function _o(e,t,n){t.updateQueue=e.updateQueue,t.flags&=-2053,e.lanes&=~n}function vo(e){if(ro){for(e=e.memoizedState;e!==null;){var t=e.queue;t!==null&&(t.pending=null),e=e.next}ro=!1}$a=0,no=to=eo=null,io=!1,so=oo=0,co=null}function yo(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return no===null?eo.memoizedState=no=e:no=no.next=e,no}function bo(){if(to===null){var e=eo.alternate;e=e===null?null:e.memoizedState}else e=to.next;var t=no===null?eo.memoizedState:no.next;if(t!==null)no=t,to=e;else{if(e===null)throw eo.alternate===null?Error(i(467)):Error(i(310));to=e,e={memoizedState:to.memoizedState,baseState:to.baseState,baseQueue:to.baseQueue,queue:to.queue,next:null},no===null?eo.memoizedState=no=e:no=no.next=e}return no}function xo(){return{lastEffect:null,events:null,stores:null,memoCache:null}}function So(e){var t=so;return so+=1,co===null&&(co=[]),e=ma(co,e,t),t=eo,(no===null?t.memoizedState:no.next)===null&&(t=t.alternate,I.H=t===null||t.memoizedState===null?ks:As),e}function Co(e){if(typeof e==`object`&&e){if(typeof e.then==`function`)return So(e);if(e.$$typeof===C)return Hi(e)}throw Error(i(438,String(e)))}function wo(e){var t=null,n=eo.updateQueue;if(n!==null&&(t=n.memoCache),t==null){var r=eo.alternate;r!==null&&(r=r.updateQueue,r!==null&&(r=r.memoCache,r!=null&&(t={data:r.data.map(function(e){return e.slice()}),index:0})))}if(t??={data:[],index:0},n===null&&(n=xo(),eo.updateQueue=n),n.memoCache=t,n=t.data[t.index],n===void 0)for(n=t.data[t.index]=Array(e),r=0;r<e;r++)n[r]=A;return t.index++,n}function To(e,t){return typeof t==`function`?t(e):t}function Eo(e){return Do(bo(),to,e)}function Do(e,t,n){var r=e.queue;if(r===null)throw Error(i(311));r.lastRenderedReducer=n;var a=e.baseQueue,o=r.pending;if(o!==null){if(a!==null){var s=a.next;a.next=o.next,o.next=s}t.baseQueue=a=o,r.pending=null}if(o=e.baseState,a===null)e.memoizedState=o;else{t=a.next;var c=s=null,l=null,u=t,d=!1;do{var f=u.lane&-536870913;if(f===u.lane?($a&f)===f:(Pl&f)===f){var p=u.revertLane;if(p===0)l!==null&&(l=l.next={lane:0,revertLane:0,gesture:null,action:u.action,hasEagerState:u.hasEagerState,eagerState:u.eagerState,next:null}),f===$i&&(d=!0);else if(($a&p)===p){u=u.next,p===$i&&(d=!0);continue}else f={lane:0,revertLane:u.revertLane,gesture:null,action:u.action,hasEagerState:u.hasEagerState,eagerState:u.eagerState,next:null},l===null?(c=l=f,s=o):l=l.next=f,eo.lanes|=p,Hl|=p;f=u.action,ao&&n(o,f),o=u.hasEagerState?u.eagerState:n(o,f)}else p={lane:f,revertLane:u.revertLane,gesture:u.gesture,action:u.action,hasEagerState:u.hasEagerState,eagerState:u.eagerState,next:null},l===null?(c=l=p,s=o):l=l.next=p,eo.lanes|=f,Hl|=f;u=u.next}while(u!==null&&u!==t);if(l===null?s=o:l.next=c,!lr(o,e.memoizedState)&&(qs=!0,d&&(n=ea,n!==null)))throw n;e.memoizedState=o,e.baseState=s,e.baseQueue=l,r.lastRenderedState=o}return a===null&&(r.lanes=0),[e.memoizedState,r.dispatch]}function Oo(e){var t=bo(),n=t.queue;if(n===null)throw Error(i(311));n.lastRenderedReducer=e;var r=n.dispatch,a=n.pending,o=t.memoizedState;if(a!==null){n.pending=null;var s=a=a.next;do o=e(o,s.action),s=s.next;while(s!==a);lr(o,t.memoizedState)||(qs=!0),t.memoizedState=o,t.baseQueue===null&&(t.baseState=o),n.lastRenderedState=o}return[o,r]}function ko(e,t,n){var r=eo,a=bo(),o=xi;if(o){if(n===void 0)throw Error(i(407));n=n()}else n=t();var s=!lr((to||a).memoizedState,n);if(s&&(a.memoizedState=n,qs=!0),a=a.queue,es(Mo.bind(null,r,a,e),[e]),a.getSnapshot!==t||s||no!==null&&no.memoizedState.tag&1){if(r.flags|=2048,Yo(9,{destroy:void 0},jo.bind(null,r,a,n,t),null),Ml===null)throw Error(i(349));o||$a&127||Ao(r,t,n)}return n}function Ao(e,t,n){e.flags|=16384,e={getSnapshot:t,value:n},t=eo.updateQueue,t===null?(t=xo(),eo.updateQueue=t,t.stores=[e]):(n=t.stores,n===null?t.stores=[e]:n.push(e))}function jo(e,t,n,r){t.value=n,t.getSnapshot=r,No(t)&&Po(e)}function Mo(e,t,n){return n(function(){No(t)&&Po(e)})}function No(e){var t=e.getSnapshot;e=e.value;try{var n=t();return!lr(e,n)}catch{return!0}}function Po(e){var t=Wr(e,2);t!==null&&fu(t,e,2)}function Fo(e){var t=yo();if(typeof e==`function`){var n=e;if(e=n(),ao){De(!0);try{n()}finally{De(!1)}}}return t.memoizedState=t.baseState=e,t.queue={pending:null,lanes:0,dispatch:null,lastRenderedReducer:To,lastRenderedState:e},t}function Io(e,t,n,r){return e.baseState=n,Do(e,to,typeof r==`function`?r:To)}function Lo(e,t,n,r,a){if(Ts(e))throw Error(i(485));if(e=t.action,e!==null){var o={payload:a,action:e,next:null,isTransition:!0,status:`pending`,value:null,reason:null,listeners:[],then:function(e){o.listeners.push(e)}};I.T===null?o.isTransition=!1:n(!0),r(o),n=t.pending,n===null?(o.next=t.pending=o,Ro(t,o)):(o.next=n.next,t.pending=n.next=o)}}function Ro(e,t){var n=t.action,r=t.payload,i=e.state;if(t.isTransition){var a=I.T,o={};I.T=o;try{var s=n(i,r),c=I.S;c!==null&&c(o,s),zo(e,t,s)}catch(n){Vo(e,t,n)}finally{a!==null&&o.types!==null&&(a.types=o.types),I.T=a}}else try{a=n(i,r),zo(e,t,a)}catch(n){Vo(e,t,n)}}function zo(e,t,n){typeof n==`object`&&n&&typeof n.then==`function`?n.then(function(n){Bo(e,t,n)},function(n){return Vo(e,t,n)}):Bo(e,t,n)}function Bo(e,t,n){t.status=`fulfilled`,t.value=n,Ho(t),e.state=n,t=e.pending,t!==null&&(n=t.next,n===t?e.pending=null:(n=n.next,t.next=n,Ro(e,n)))}function Vo(e,t,n){var r=e.pending;if(e.pending=null,r!==null){r=r.next;do t.status=`rejected`,t.reason=n,Ho(t),t=t.next;while(t!==r)}e.action=null}function Ho(e){e=e.listeners;for(var t=0;t<e.length;t++)(0,e[t])()}function Uo(e,t){return t}function Wo(e,t){if(xi){var n=Ml.formState;if(n!==null){a:{var r=eo;if(xi){if(bi){b:{for(var i=bi,a=Ci;i.nodeType!==8;){if(!a){i=null;break b}if(i=cf(i.nextSibling),i===null){i=null;break b}}a=i.data,i=a===`F!`||a===`F`?i:null}if(i){bi=cf(i.nextSibling),r=i.data===`F!`;break a}}Ti(r)}r=!1}r&&(t=n[0])}}return n=yo(),n.memoizedState=n.baseState=t,r={pending:null,lanes:0,dispatch:null,lastRenderedReducer:Uo,lastRenderedState:t},n.queue=r,n=Ss.bind(null,eo,r),r.dispatch=n,r=Fo(!1),a=ws.bind(null,eo,!1,r.queue),r=yo(),i={state:t,dispatch:null,action:e,pending:null},r.queue=i,n=Lo.bind(null,eo,i,a,n),i.dispatch=n,r.memoizedState=e,[t,n,!1]}function Go(e){return Ko(bo(),to,e)}function Ko(e,t,n){if(t=Do(e,t,Uo)[0],e=Eo(To)[0],typeof t==`object`&&t&&typeof t.then==`function`)try{var r=So(t)}catch(e){throw e===la?da:e}else r=t;t=bo();var i=t.queue,a=i.dispatch;return n!==t.memoizedState&&(eo.flags|=2048,Yo(9,{destroy:void 0},qo.bind(null,i,n),null)),[r,a,e]}function qo(e,t){e.action=t}function Jo(e){var t=bo(),n=to;if(n!==null)return Ko(t,n,e);bo(),t=t.memoizedState,n=bo();var r=n.queue.dispatch;return n.memoizedState=e,[t,r,!1]}function Yo(e,t,n,r){return e={tag:e,create:n,deps:r,inst:t,next:null},t=eo.updateQueue,t===null&&(t=xo(),eo.updateQueue=t),n=t.lastEffect,n===null?t.lastEffect=e.next=e:(r=n.next,n.next=e,e.next=r,t.lastEffect=e),e}function Xo(){return bo().memoizedState}function Zo(e,t,n,r){var i=yo();eo.flags|=e,i.memoizedState=Yo(1|t,{destroy:void 0},n,r===void 0?null:r)}function Qo(e,t,n,r){var i=bo();r=r===void 0?null:r;var a=i.memoizedState.inst;to!==null&&r!==null&&uo(r,to.memoizedState.deps)?i.memoizedState=Yo(t,a,n,r):(eo.flags|=e,i.memoizedState=Yo(1|t,a,n,r))}function $o(e,t){Zo(8390656,8,e,t)}function es(e,t){Qo(2048,8,e,t)}function ts(e){eo.flags|=4;var t=eo.updateQueue;if(t===null)t=xo(),eo.updateQueue=t,t.events=[e];else{var n=t.events;n===null?t.events=[e]:n.push(e)}}function ns(e){var t=bo().memoizedState;return ts({ref:t,nextImpl:e}),function(){if(jl&2)throw Error(i(440));return t.impl.apply(void 0,arguments)}}function rs(e,t){return Qo(4,2,e,t)}function is(e,t){return Qo(4,4,e,t)}function as(e,t){if(typeof t==`function`){e=e();var n=t(e);return function(){typeof n==`function`?n():t(null)}}if(t!=null)return e=e(),t.current=e,function(){t.current=null}}function os(e,t,n){n=n==null?null:n.concat([e]),Qo(4,4,as.bind(null,t,e),n)}function ss(){}function cs(e,t){var n=bo();t=t===void 0?null:t;var r=n.memoizedState;return t!==null&&uo(t,r[1])?r[0]:(n.memoizedState=[e,t],e)}function ls(e,t){var n=bo();t=t===void 0?null:t;var r=n.memoizedState;if(t!==null&&uo(t,r[1]))return r[0];if(r=e(),ao){De(!0);try{e()}finally{De(!1)}}return n.memoizedState=[r,t],r}function us(e,t,n){return n===void 0||$a&1073741824&&!(Pl&261930)?e.memoizedState=t:(e.memoizedState=n,e=du(),eo.lanes|=e,Hl|=e,n)}function ds(e,t,n,r){return lr(n,t)?n:za.current===null?!($a&42)||$a&1073741824&&!(Pl&261930)?(qs=!0,e.memoizedState=n):(e=du(),eo.lanes|=e,Hl|=e,t):(e=us(e,n,r),lr(e,t)||(qs=!0),e)}function fs(e,t,n,r,i){var a=L.p;L.p=a!==0&&8>a?a:8;var o=I.T,s={};I.T=s,ws(e,!1,t,n);try{var c=i(),l=I.S;l!==null&&l(s,c),typeof c==`object`&&c&&typeof c.then==`function`?Cs(e,t,ra(c,r),uu(e)):Cs(e,t,r,uu(e))}catch(n){Cs(e,t,{then:function(){},status:`rejected`,reason:n},uu())}finally{L.p=a,o!==null&&s.types!==null&&(o.types=s.types),I.T=o}}function ps(){}function ms(e,t,n,r){if(e.tag!==5)throw Error(i(476));var a=hs(e).queue;fs(e,a,t,R,n===null?ps:function(){return gs(e),n(r)})}function hs(e){var t=e.memoizedState;if(t!==null)return t;t={memoizedState:R,baseState:R,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:To,lastRenderedState:R},next:null};var n={};return t.next={memoizedState:n,baseState:n,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:To,lastRenderedState:n},next:null},e.memoizedState=t,e=e.alternate,e!==null&&(e.memoizedState=t),t}function gs(e){var t=hs(e);t.next===null&&(t=e.alternate.memoizedState),Cs(e,t.next.queue,{},uu())}function _s(){return Hi(Qf)}function vs(){return bo().memoizedState}function ys(){return bo().memoizedState}function bs(e){for(var t=e.return;t!==null;){switch(t.tag){case 24:case 3:var n=uu();e=Aa(n);var r=ja(t,e,n);r!==null&&(fu(r,t,n),Ma(r,t,n)),t={cache:Yi()},e.payload=t;return}t=t.return}}function xs(e,t,n){var r=uu();n={lane:r,revertLane:0,gesture:null,action:n,hasEagerState:!1,eagerState:null,next:null},Ts(e)?Es(t,n):(n=Ur(e,t,n,r),n!==null&&(fu(n,e,r),Ds(n,t,r)))}function Ss(e,t,n){Cs(e,t,n,uu())}function Cs(e,t,n,r){var i={lane:r,revertLane:0,gesture:null,action:n,hasEagerState:!1,eagerState:null,next:null};if(Ts(e))Es(t,i);else{var a=e.alternate;if(e.lanes===0&&(a===null||a.lanes===0)&&(a=t.lastRenderedReducer,a!==null))try{var o=t.lastRenderedState,s=a(o,n);if(i.hasEagerState=!0,i.eagerState=s,lr(s,o))return Hr(e,t,i,0),Ml===null&&Vr(),!1}catch{}if(n=Ur(e,t,i,r),n!==null)return fu(n,e,r),Ds(n,t,r),!0}return!1}function ws(e,t,n,r){if(r={lane:2,revertLane:ld(),gesture:null,action:r,hasEagerState:!1,eagerState:null,next:null},Ts(e)){if(t)throw Error(i(479))}else t=Ur(e,n,r,2),t!==null&&fu(t,e,2)}function Ts(e){var t=e.alternate;return e===eo||t!==null&&t===eo}function Es(e,t){io=ro=!0;var n=e.pending;n===null?t.next=t:(t.next=n.next,n.next=t),e.pending=t}function Ds(e,t,n){if(n&4194048){var r=t.lanes;r&=e.pendingLanes,n|=r,t.lanes=n,We(e,n)}}var Os={readContext:Hi,use:Co,useCallback:$,useContext:$,useEffect:$,useImperativeHandle:$,useLayoutEffect:$,useInsertionEffect:$,useMemo:$,useReducer:$,useRef:$,useState:$,useDebugValue:$,useDeferredValue:$,useTransition:$,useSyncExternalStore:$,useId:$,useHostTransitionStatus:$,useFormState:$,useActionState:$,useOptimistic:$,useMemoCache:$,useCacheRefresh:$};Os.useEffectEvent=$;var ks={readContext:Hi,use:Co,useCallback:function(e,t){return yo().memoizedState=[e,t===void 0?null:t],e},useContext:Hi,useEffect:$o,useImperativeHandle:function(e,t,n){n=n==null?null:n.concat([e]),Zo(4194308,4,as.bind(null,t,e),n)},useLayoutEffect:function(e,t){return Zo(4194308,4,e,t)},useInsertionEffect:function(e,t){Zo(4,2,e,t)},useMemo:function(e,t){var n=yo();t=t===void 0?null:t;var r=e();if(ao){De(!0);try{e()}finally{De(!1)}}return n.memoizedState=[r,t],r},useReducer:function(e,t,n){var r=yo();if(n!==void 0){var i=n(t);if(ao){De(!0);try{n(t)}finally{De(!1)}}}else i=t;return r.memoizedState=r.baseState=i,e={pending:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:i},r.queue=e,e=e.dispatch=xs.bind(null,eo,e),[r.memoizedState,e]},useRef:function(e){var t=yo();return e={current:e},t.memoizedState=e},useState:function(e){e=Fo(e);var t=e.queue,n=Ss.bind(null,eo,t);return t.dispatch=n,[e.memoizedState,n]},useDebugValue:ss,useDeferredValue:function(e,t){return us(yo(),e,t)},useTransition:function(){var e=Fo(!1);return e=fs.bind(null,eo,e.queue,!0,!1),yo().memoizedState=e,[!1,e]},useSyncExternalStore:function(e,t,n){var r=eo,a=yo();if(xi){if(n===void 0)throw Error(i(407));n=n()}else{if(n=t(),Ml===null)throw Error(i(349));Pl&127||Ao(r,t,n)}a.memoizedState=n;var o={value:n,getSnapshot:t};return a.queue=o,$o(Mo.bind(null,r,o,e),[e]),r.flags|=2048,Yo(9,{destroy:void 0},jo.bind(null,r,o,n,t),null),n},useId:function(){var e=yo(),t=Ml.identifierPrefix;if(xi){var n=pi,r=fi;n=(r&~(1<<32-Oe(r)-1)).toString(32)+n,t=`_`+t+`R_`+n,n=oo++,0<n&&(t+=`H`+n.toString(32)),t+=`_`}else n=lo++,t=`_`+t+`r_`+n.toString(32)+`_`;return e.memoizedState=t},useHostTransitionStatus:_s,useFormState:Wo,useActionState:Wo,useOptimistic:function(e){var t=yo();t.memoizedState=t.baseState=e;var n={pending:null,lanes:0,dispatch:null,lastRenderedReducer:null,lastRenderedState:null};return t.queue=n,t=ws.bind(null,eo,!0,n),n.dispatch=t,[e,t]},useMemoCache:wo,useCacheRefresh:function(){return yo().memoizedState=bs.bind(null,eo)},useEffectEvent:function(e){var t=yo(),n={impl:e};return t.memoizedState=n,function(){if(jl&2)throw Error(i(440));return n.impl.apply(void 0,arguments)}}},As={readContext:Hi,use:Co,useCallback:cs,useContext:Hi,useEffect:es,useImperativeHandle:os,useInsertionEffect:rs,useLayoutEffect:is,useMemo:ls,useReducer:Eo,useRef:Xo,useState:function(){return Eo(To)},useDebugValue:ss,useDeferredValue:function(e,t){return ds(bo(),to.memoizedState,e,t)},useTransition:function(){var e=Eo(To)[0],t=bo().memoizedState;return[typeof e==`boolean`?e:So(e),t]},useSyncExternalStore:ko,useId:vs,useHostTransitionStatus:_s,useFormState:Go,useActionState:Go,useOptimistic:function(e,t){return Io(bo(),to,e,t)},useMemoCache:wo,useCacheRefresh:ys};As.useEffectEvent=ns;var js={readContext:Hi,use:Co,useCallback:cs,useContext:Hi,useEffect:es,useImperativeHandle:os,useInsertionEffect:rs,useLayoutEffect:is,useMemo:ls,useReducer:Oo,useRef:Xo,useState:function(){return Oo(To)},useDebugValue:ss,useDeferredValue:function(e,t){var n=bo();return to===null?us(n,e,t):ds(n,to.memoizedState,e,t)},useTransition:function(){var e=Oo(To)[0],t=bo().memoizedState;return[typeof e==`boolean`?e:So(e),t]},useSyncExternalStore:ko,useId:vs,useHostTransitionStatus:_s,useFormState:Jo,useActionState:Jo,useOptimistic:function(e,t){var n=bo();return to===null?(n.baseState=e,[e,n.queue.dispatch]):Io(n,to,e,t)},useMemoCache:wo,useCacheRefresh:ys};js.useEffectEvent=ns;function Ms(e,t,n,r){t=e.memoizedState,n=n(r,t),n=n==null?t:h({},t,n),e.memoizedState=n,e.lanes===0&&(e.updateQueue.baseState=n)}var Ns={enqueueSetState:function(e,t,n){e=e._reactInternals;var r=uu(),i=Aa(r);i.payload=t,n!=null&&(i.callback=n),t=ja(e,i,r),t!==null&&(fu(t,e,r),Ma(t,e,r))},enqueueReplaceState:function(e,t,n){e=e._reactInternals;var r=uu(),i=Aa(r);i.tag=1,i.payload=t,n!=null&&(i.callback=n),t=ja(e,i,r),t!==null&&(fu(t,e,r),Ma(t,e,r))},enqueueForceUpdate:function(e,t){e=e._reactInternals;var n=uu(),r=Aa(n);r.tag=2,t!=null&&(r.callback=t),t=ja(e,r,n),t!==null&&(fu(t,e,n),Ma(t,e,n))}};function Ps(e,t,n,r,i,a,o){return e=e.stateNode,typeof e.shouldComponentUpdate==`function`?e.shouldComponentUpdate(r,a,o):t.prototype&&t.prototype.isPureReactComponent?!ur(n,r)||!ur(i,a):!0}function Fs(e,t,n,r){e=t.state,typeof t.componentWillReceiveProps==`function`&&t.componentWillReceiveProps(n,r),typeof t.UNSAFE_componentWillReceiveProps==`function`&&t.UNSAFE_componentWillReceiveProps(n,r),t.state!==e&&Ns.enqueueReplaceState(t,t.state,null)}function Is(e,t){var n=t;if(`ref`in t)for(var r in n={},t)r!==`ref`&&(n[r]=t[r]);if(e=e.defaultProps)for(var i in n===t&&(n=h({},n)),e)n[i]===void 0&&(n[i]=e[i]);return n}function Ls(e){Lr(e)}function Rs(e){console.error(e)}function zs(e){Lr(e)}function Bs(e,t){try{var n=e.onUncaughtError;n(t.value,{componentStack:t.stack})}catch(e){setTimeout(function(){throw e})}}function Vs(e,t,n){try{var r=e.onCaughtError;r(n.value,{componentStack:n.stack,errorBoundary:t.tag===1?t.stateNode:null})}catch(e){setTimeout(function(){throw e})}}function Hs(e,t,n){return n=Aa(n),n.tag=3,n.payload={element:null},n.callback=function(){Bs(e,t)},n}function Us(e){return e=Aa(e),e.tag=3,e}function Ws(e,t,n,r){var i=n.type.getDerivedStateFromError;if(typeof i==`function`){var a=r.value;e.payload=function(){return i(a)},e.callback=function(){Vs(t,n,r)}}var o=n.stateNode;o!==null&&typeof o.componentDidCatch==`function`&&(e.callback=function(){Vs(t,n,r),typeof i!=`function`&&(eu===null?eu=new Set([this]):eu.add(this));var e=r.stack;this.componentDidCatch(r.value,{componentStack:e===null?``:e})})}function Gs(e,t,n,r,a){if(n.flags|=32768,typeof r==`object`&&r&&typeof r.then==`function`){if(t=n.alternate,t!==null&&zi(t,n,a,!0),n=Wa.current,n!==null){switch(n.tag){case 31:case 13:return Ga===null?wu():n.alternate===null&&Vl===0&&(Vl=3),n.flags&=-257,n.flags|=65536,n.lanes=a,r===fa?n.flags|=16384:(t=n.updateQueue,t===null?n.updateQueue=new Set([r]):t.add(r),Uu(e,r,a)),!1;case 22:return n.flags|=65536,r===fa?n.flags|=16384:(t=n.updateQueue,t===null?(t={transitions:null,markerInstances:null,retryQueue:new Set([r])},n.updateQueue=t):(n=t.retryQueue,n===null?t.retryQueue=new Set([r]):n.add(r)),Uu(e,r,a)),!1}throw Error(i(435,n.tag))}return Uu(e,r,a),wu(),!1}if(xi)return t=Wa.current,t===null?(r!==wi&&(t=Error(i(423),{cause:r}),ji(ii(t,n))),e=e.current.alternate,e.flags|=65536,a&=-a,e.lanes|=a,r=ii(r,n),a=Hs(e.stateNode,r,a),Na(e,a),Vl!==4&&(Vl=2)):(!(t.flags&65536)&&(t.flags|=256),t.flags|=65536,t.lanes=a,r!==wi&&(e=Error(i(422),{cause:r}),ji(ii(e,n)))),!1;var o=Error(i(520),{cause:r});if(o=ii(o,n),ql===null?ql=[o]:ql.push(o),Vl!==4&&(Vl=2),t===null)return!0;r=ii(r,n),n=t;do{switch(n.tag){case 3:return n.flags|=65536,e=a&-a,n.lanes|=e,e=Hs(n.stateNode,r,e),Na(n,e),!1;case 1:if(t=n.type,o=n.stateNode,!(n.flags&128)&&(typeof t.getDerivedStateFromError==`function`||o!==null&&typeof o.componentDidCatch==`function`&&(eu===null||!eu.has(o))))return n.flags|=65536,a&=-a,n.lanes|=a,a=Us(a),Ws(a,e,n,r),Na(n,a),!1}n=n.return}while(n!==null);return!1}var Ks=Error(i(461)),qs=!1;function Js(e,t,n,r){t.child=e===null?Ea(t,null,n,r):Ta(t,e.child,n,r)}function Ys(e,t,n,r,i){n=n.render;var a=t.ref;if(`ref`in r){var o={};for(var s in r)s!==`ref`&&(o[s]=r[s])}else o=r;return Vi(t),r=fo(e,t,n,o,a,i),s=go(),e!==null&&!qs?(_o(e,t,i),yc(e,t,i)):(xi&&s&&gi(t),t.flags|=1,Js(e,t,r,i),t.child)}function Xs(e,t,n,r,i){if(e===null){var a=n.type;return typeof a==`function`&&!Xr(a)&&a.defaultProps===void 0&&n.compare===null?(t.tag=15,t.type=a,Zs(e,t,a,r,i)):(e=$r(n.type,null,r,t,t.mode,i),e.ref=t.ref,e.return=t,t.child=e)}if(a=e.child,!bc(e,i)){var o=a.memoizedProps;if(n=n.compare,n=n===null?ur:n,n(o,r)&&e.ref===t.ref)return yc(e,t,i)}return t.flags|=1,e=Zr(a,r),e.ref=t.ref,e.return=t,t.child=e}function Zs(e,t,n,r,i){if(e!==null){var a=e.memoizedProps;if(ur(a,r)&&e.ref===t.ref){if(qs=!1,t.pendingProps=r=a,bc(e,i))e.flags&131072&&(qs=!0);else return t.lanes=e.lanes,yc(e,t,i)}}return ac(e,t,n,r,i)}function Qs(e,t,n,r){var i=r.children,a=e===null?null:e.memoizedState;if(e===null&&t.stateNode===null&&(t.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null}),r.mode===`hidden`){if(t.flags&128){if(a=a===null?n:a.baseLanes|n,e!==null){for(r=t.child=e.child,i=0;r!==null;)i=i|r.lanes|r.childLanes,r=r.sibling;r=i&~a}else r=0,t.child=null;return ec(e,t,a,n,r)}if(n&536870912)t.memoizedState={baseLanes:0,cachePool:null},e!==null&&sa(t,a===null?null:a.cachePool),a===null?Ha():Va(t,a),Ja(t);else return r=t.lanes=536870912,ec(e,t,a===null?n:a.baseLanes|n,n,r)}else a===null?(e!==null&&sa(t,null),Ha(),Ya(t)):(sa(t,a.cachePool),Va(t,a),Ya(t),t.memoizedState=null);return Js(e,t,i,n),t.child}function $s(e,t){return e!==null&&e.tag===22||t.stateNode!==null||(t.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null}),t.sibling}function ec(e,t,n,r,i){var a=oa();return a=a===null?null:{parent:Ji._currentValue,pool:a},t.memoizedState={baseLanes:n,cachePool:a},e!==null&&sa(t,null),Ha(),Ja(t),e!==null&&zi(e,t,r,!0),t.childLanes=i,null}function tc(e,t){return t=mc({mode:t.mode,children:t.children},e.mode),t.ref=e.ref,e.child=t,t.return=e,t}function nc(e,t,n){return Ta(t,e.child,null,n),e=tc(t,t.pendingProps),e.flags|=2,Xa(t),t.memoizedState=null,e}function rc(e,t,n){var r=t.pendingProps,a=!!(t.flags&128);if(t.flags&=-129,e===null){if(xi){if(r.mode===`hidden`)return e=tc(t,r),t.lanes=536870912,$s(null,e);if(qa(t),(e=bi)?(e=rf(e,Ci),e=e!==null&&e.data===`&`?e:null,e!==null&&(t.memoizedState={dehydrated:e,treeContext:di===null?null:{id:fi,overflow:pi},retryLane:536870912,hydrationErrors:null},n=ni(e),n.return=t,t.child=n,yi=t,bi=null)):e=null,e===null)throw Ti(t);return t.lanes=536870912,null}return tc(t,r)}var o=e.memoizedState;if(o!==null){var s=o.dehydrated;if(qa(t),a){if(t.flags&256)t.flags&=-257,t=nc(e,t,n);else if(t.memoizedState!==null)t.child=e.child,t.flags|=128,t=null;else throw Error(i(558))}else if(qs||zi(e,t,n,!1),a=(n&e.childLanes)!==0,qs||a){if(r=Ml,r!==null&&(s=Ge(r,n),s!==0&&s!==o.retryLane))throw o.retryLane=s,Wr(e,s),fu(r,e,s),Ks;wu(),t=nc(e,t,n)}else e=o.treeContext,bi=cf(s.nextSibling),yi=t,xi=!0,Si=null,Ci=!1,e!==null&&vi(t,e),t=tc(t,r),t.flags|=4096;return t}return e=Zr(e.child,{mode:r.mode,children:r.children}),e.ref=t.ref,t.child=e,e.return=t,e}function ic(e,t){var n=t.ref;if(n===null)e!==null&&e.ref!==null&&(t.flags|=4194816);else{if(typeof n!=`function`&&typeof n!=`object`)throw Error(i(284));(e===null||e.ref!==n)&&(t.flags|=4194816)}}function ac(e,t,n,r,i){return Vi(t),n=fo(e,t,n,r,void 0,i),r=go(),e!==null&&!qs?(_o(e,t,i),yc(e,t,i)):(xi&&r&&gi(t),t.flags|=1,Js(e,t,n,i),t.child)}function oc(e,t,n,r,i,a){return Vi(t),t.updateQueue=null,n=mo(t,r,n,i),po(e),r=go(),e!==null&&!qs?(_o(e,t,a),yc(e,t,a)):(xi&&r&&gi(t),t.flags|=1,Js(e,t,n,a),t.child)}function sc(e,t,n,r,i){if(Vi(t),t.stateNode===null){var a=qr,o=n.contextType;typeof o==`object`&&o&&(a=Hi(o)),a=new n(r,a),t.memoizedState=a.state!==null&&a.state!==void 0?a.state:null,a.updater=Ns,t.stateNode=a,a._reactInternals=t,a=t.stateNode,a.props=r,a.state=t.memoizedState,a.refs={},Oa(t),o=n.contextType,a.context=typeof o==`object`&&o?Hi(o):qr,a.state=t.memoizedState,o=n.getDerivedStateFromProps,typeof o==`function`&&(Ms(t,n,o,r),a.state=t.memoizedState),typeof n.getDerivedStateFromProps==`function`||typeof a.getSnapshotBeforeUpdate==`function`||typeof a.UNSAFE_componentWillMount!=`function`&&typeof a.componentWillMount!=`function`||(o=a.state,typeof a.componentWillMount==`function`&&a.componentWillMount(),typeof a.UNSAFE_componentWillMount==`function`&&a.UNSAFE_componentWillMount(),o!==a.state&&Ns.enqueueReplaceState(a,a.state,null),Ia(t,r,a,i),Fa(),a.state=t.memoizedState),typeof a.componentDidMount==`function`&&(t.flags|=4194308),r=!0}else if(e===null){a=t.stateNode;var s=t.memoizedProps,c=Is(n,s);a.props=c;var l=a.context,u=n.contextType;o=qr,typeof u==`object`&&u&&(o=Hi(u));var d=n.getDerivedStateFromProps;u=typeof d==`function`||typeof a.getSnapshotBeforeUpdate==`function`,s=t.pendingProps!==s,u||typeof a.UNSAFE_componentWillReceiveProps!=`function`&&typeof a.componentWillReceiveProps!=`function`||(s||l!==o)&&Fs(t,a,r,o),Da=!1;var f=t.memoizedState;a.state=f,Ia(t,r,a,i),Fa(),l=t.memoizedState,s||f!==l||Da?(typeof d==`function`&&(Ms(t,n,d,r),l=t.memoizedState),(c=Da||Ps(t,n,c,r,f,l,o))?(u||typeof a.UNSAFE_componentWillMount!=`function`&&typeof a.componentWillMount!=`function`||(typeof a.componentWillMount==`function`&&a.componentWillMount(),typeof a.UNSAFE_componentWillMount==`function`&&a.UNSAFE_componentWillMount()),typeof a.componentDidMount==`function`&&(t.flags|=4194308)):(typeof a.componentDidMount==`function`&&(t.flags|=4194308),t.memoizedProps=r,t.memoizedState=l),a.props=r,a.state=l,a.context=o,r=c):(typeof a.componentDidMount==`function`&&(t.flags|=4194308),r=!1)}else{a=t.stateNode,ka(e,t),o=t.memoizedProps,u=Is(n,o),a.props=u,d=t.pendingProps,f=a.context,l=n.contextType,c=qr,typeof l==`object`&&l&&(c=Hi(l)),s=n.getDerivedStateFromProps,(l=typeof s==`function`||typeof a.getSnapshotBeforeUpdate==`function`)||typeof a.UNSAFE_componentWillReceiveProps!=`function`&&typeof a.componentWillReceiveProps!=`function`||(o!==d||f!==c)&&Fs(t,a,r,c),Da=!1,f=t.memoizedState,a.state=f,Ia(t,r,a,i),Fa();var p=t.memoizedState;o!==d||f!==p||Da||e!==null&&e.dependencies!==null&&Bi(e.dependencies)?(typeof s==`function`&&(Ms(t,n,s,r),p=t.memoizedState),(u=Da||Ps(t,n,u,r,f,p,c)||e!==null&&e.dependencies!==null&&Bi(e.dependencies))?(l||typeof a.UNSAFE_componentWillUpdate!=`function`&&typeof a.componentWillUpdate!=`function`||(typeof a.componentWillUpdate==`function`&&a.componentWillUpdate(r,p,c),typeof a.UNSAFE_componentWillUpdate==`function`&&a.UNSAFE_componentWillUpdate(r,p,c)),typeof a.componentDidUpdate==`function`&&(t.flags|=4),typeof a.getSnapshotBeforeUpdate==`function`&&(t.flags|=1024)):(typeof a.componentDidUpdate!=`function`||o===e.memoizedProps&&f===e.memoizedState||(t.flags|=4),typeof a.getSnapshotBeforeUpdate!=`function`||o===e.memoizedProps&&f===e.memoizedState||(t.flags|=1024),t.memoizedProps=r,t.memoizedState=p),a.props=r,a.state=p,a.context=c,r=u):(typeof a.componentDidUpdate!=`function`||o===e.memoizedProps&&f===e.memoizedState||(t.flags|=4),typeof a.getSnapshotBeforeUpdate!=`function`||o===e.memoizedProps&&f===e.memoizedState||(t.flags|=1024),r=!1)}return a=r,ic(e,t),r=!!(t.flags&128),a||r?(a=t.stateNode,n=r&&typeof n.getDerivedStateFromError!=`function`?null:a.render(),t.flags|=1,e!==null&&r?(t.child=Ta(t,e.child,null,i),t.child=Ta(t,null,n,i)):Js(e,t,n,i),t.memoizedState=a.state,e=t.child):e=yc(e,t,i),e}function cc(e,t,n,r){return ki(),t.flags|=256,Js(e,t,n,r),t.child}var lc={dehydrated:null,treeContext:null,retryLane:0,hydrationErrors:null};function uc(e){return{baseLanes:e,cachePool:ca()}}function dc(e,t,n){return e=e===null?0:e.childLanes&~n,t&&(e|=Gl),e}function fc(e,t,n){var r=t.pendingProps,a=!1,o=!!(t.flags&128),s;if((s=o)||(s=e!==null&&e.memoizedState===null?!1:!!(Za.current&2)),s&&(a=!0,t.flags&=-129),s=!!(t.flags&32),t.flags&=-33,e===null){if(xi){if(a?Ka(t):Ya(t),(e=bi)?(e=rf(e,Ci),e=e!==null&&e.data!==`&`?e:null,e!==null&&(t.memoizedState={dehydrated:e,treeContext:di===null?null:{id:fi,overflow:pi},retryLane:536870912,hydrationErrors:null},n=ni(e),n.return=t,t.child=n,yi=t,bi=null)):e=null,e===null)throw Ti(t);return of(e)?t.lanes=32:t.lanes=536870912,null}var c=r.children;return r=r.fallback,a?(Ya(t),a=t.mode,c=mc({mode:`hidden`,children:c},a),r=ei(r,a,n,null),c.return=t,r.return=t,c.sibling=r,t.child=c,r=t.child,r.memoizedState=uc(n),r.childLanes=dc(e,s,n),t.memoizedState=lc,$s(null,r)):(Ka(t),pc(t,c))}var l=e.memoizedState;if(l!==null&&(c=l.dehydrated,c!==null)){if(o)t.flags&256?(Ka(t),t.flags&=-257,t=hc(e,t,n)):t.memoizedState===null?(Ya(t),c=r.fallback,a=t.mode,r=mc({mode:`visible`,children:r.children},a),c=ei(c,a,n,null),c.flags|=2,r.return=t,c.return=t,r.sibling=c,t.child=r,Ta(t,e.child,null,n),r=t.child,r.memoizedState=uc(n),r.childLanes=dc(e,s,n),t.memoizedState=lc,t=$s(null,r)):(Ya(t),t.child=e.child,t.flags|=128,t=null);else if(Ka(t),of(c)){if(s=c.nextSibling&&c.nextSibling.dataset,s)var u=s.dgst;s=u,r=Error(i(419)),r.stack=``,r.digest=s,ji({value:r,source:null,stack:null}),t=hc(e,t,n)}else if(qs||zi(e,t,n,!1),s=(n&e.childLanes)!==0,qs||s){if(s=Ml,s!==null&&(r=Ge(s,n),r!==0&&r!==l.retryLane))throw l.retryLane=r,Wr(e,r),fu(s,e,r),Ks;af(c)||wu(),t=hc(e,t,n)}else af(c)?(t.flags|=192,t.child=e.child,t=null):(e=l.treeContext,bi=cf(c.nextSibling),yi=t,xi=!0,Si=null,Ci=!1,e!==null&&vi(t,e),t=pc(t,r.children),t.flags|=4096);return t}return a?(Ya(t),c=r.fallback,a=t.mode,l=e.child,u=l.sibling,r=Zr(l,{mode:`hidden`,children:r.children}),r.subtreeFlags=l.subtreeFlags&65011712,u===null?(c=ei(c,a,n,null),c.flags|=2):c=Zr(u,c),c.return=t,r.return=t,r.sibling=c,t.child=r,$s(null,r),r=t.child,c=e.child.memoizedState,c===null?c=uc(n):(a=c.cachePool,a===null?a=ca():(l=Ji._currentValue,a=a.parent===l?a:{parent:l,pool:l}),c={baseLanes:c.baseLanes|n,cachePool:a}),r.memoizedState=c,r.childLanes=dc(e,s,n),t.memoizedState=lc,$s(e.child,r)):(Ka(t),n=e.child,e=n.sibling,n=Zr(n,{mode:`visible`,children:r.children}),n.return=t,n.sibling=null,e!==null&&(s=t.deletions,s===null?(t.deletions=[e],t.flags|=16):s.push(e)),t.child=n,t.memoizedState=null,n)}function pc(e,t){return t=mc({mode:`visible`,children:t},e.mode),t.return=e,e.child=t}function mc(e,t){return e=Yr(22,e,null,t),e.lanes=0,e}function hc(e,t,n){return Ta(t,e.child,null,n),e=pc(t,t.pendingProps.children),e.flags|=2,t.memoizedState=null,e}function gc(e,t,n){e.lanes|=t;var r=e.alternate;r!==null&&(r.lanes|=t),Li(e.return,t,n)}function _c(e,t,n,r,i,a){var o=e.memoizedState;o===null?e.memoizedState={isBackwards:t,rendering:null,renderingStartTime:0,last:r,tail:n,tailMode:i,treeForkCount:a}:(o.isBackwards=t,o.rendering=null,o.renderingStartTime=0,o.last=r,o.tail=n,o.tailMode=i,o.treeForkCount=a)}function vc(e,t,n){var r=t.pendingProps,i=r.revealOrder,a=r.tail;r=r.children;var o=Za.current,s=!!(o&2);if(s?(o=o&1|2,t.flags|=128):o&=1,U(Za,o),Js(e,t,r,n),r=xi?ci:0,!s&&e!==null&&e.flags&128)a:for(e=t.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&gc(e,n,t);else if(e.tag===19)gc(e,n,t);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===t)break a;for(;e.sibling===null;){if(e.return===null||e.return===t)break a;e=e.return}e.sibling.return=e.return,e=e.sibling}switch(i){case`forwards`:for(n=t.child,i=null;n!==null;)e=n.alternate,e!==null&&Qa(e)===null&&(i=n),n=n.sibling;n=i,n===null?(i=t.child,t.child=null):(i=n.sibling,n.sibling=null),_c(t,!1,i,n,a,r);break;case`backwards`:case`unstable_legacy-backwards`:for(n=null,i=t.child,t.child=null;i!==null;){if(e=i.alternate,e!==null&&Qa(e)===null){t.child=i;break}e=i.sibling,i.sibling=n,n=i,i=e}_c(t,!0,n,null,a,r);break;case`together`:_c(t,!1,null,null,void 0,r);break;default:t.memoizedState=null}return t.child}function yc(e,t,n){if(e!==null&&(t.dependencies=e.dependencies),Hl|=t.lanes,(n&t.childLanes)===0){if(e!==null){if(zi(e,t,n,!1),(n&t.childLanes)===0)return null}else return null}if(e!==null&&t.child!==e.child)throw Error(i(153));if(t.child!==null){for(e=t.child,n=Zr(e,e.pendingProps),t.child=n,n.return=t;e.sibling!==null;)e=e.sibling,n=n.sibling=Zr(e,e.pendingProps),n.return=t;n.sibling=null}return t.child}function bc(e,t){return(e.lanes&t)!==0||(e=e.dependencies,!!(e!==null&&Bi(e)))}function xc(e,t,n){switch(t.tag){case 3:ne(t,t.stateNode.containerInfo),Fi(t,Ji,e.memoizedState.cache),ki();break;case 27:case 5:ie(t);break;case 4:ne(t,t.stateNode.containerInfo);break;case 10:Fi(t,t.type,t.memoizedProps.value);break;case 31:if(t.memoizedState!==null)return t.flags|=128,qa(t),null;break;case 13:var r=t.memoizedState;if(r!==null)return r.dehydrated===null?(n&t.child.childLanes)===0?(Ka(t),e=yc(e,t,n),e===null?null:e.sibling):fc(e,t,n):(Ka(t),t.flags|=128,null);Ka(t);break;case 19:var i=!!(e.flags&128);if(r=(n&t.childLanes)!==0,r||=(zi(e,t,n,!1),(n&t.childLanes)!==0),i){if(r)return vc(e,t,n);t.flags|=128}if(i=t.memoizedState,i!==null&&(i.rendering=null,i.tail=null,i.lastEffect=null),U(Za,Za.current),r)break;return null;case 22:return t.lanes=0,Qs(e,t,n,t.pendingProps);case 24:Fi(t,Ji,e.memoizedState.cache)}return yc(e,t,n)}function Sc(e,t,n){if(e!==null){if(e.memoizedProps!==t.pendingProps)qs=!0;else{if(!bc(e,n)&&!(t.flags&128))return qs=!1,xc(e,t,n);qs=!!(e.flags&131072)}}else qs=!1,xi&&t.flags&1048576&&hi(t,ci,t.index);switch(t.lanes=0,t.tag){case 16:a:{var r=t.pendingProps;if(e=ha(t.elementType),t.type=e,typeof e==`function`)Xr(e)?(r=Is(e,r),t.tag=1,t=sc(null,t,e,r,n)):(t.tag=0,t=ac(null,t,e,r,n));else{if(e!=null){var a=e.$$typeof;if(a===w){t.tag=11,t=Ys(null,t,e,r,n);break a}if(a===D){t.tag=14,t=Xs(null,t,e,r,n);break a}}throw t=P(e)||e,Error(i(306,t,``))}}return t;case 0:return ac(e,t,t.type,t.pendingProps,n);case 1:return r=t.type,a=Is(r,t.pendingProps),sc(e,t,r,a,n);case 3:a:{if(ne(t,t.stateNode.containerInfo),e===null)throw Error(i(387));r=t.pendingProps;var o=t.memoizedState;a=o.element,ka(e,t),Ia(t,r,null,n);var s=t.memoizedState;if(r=s.cache,Fi(t,Ji,r),r!==o.cache&&Ri(t,[Ji],n,!0),Fa(),r=s.element,o.isDehydrated){if(o={element:r,isDehydrated:!1,cache:s.cache},t.updateQueue.baseState=o,t.memoizedState=o,t.flags&256){t=cc(e,t,r,n);break a}if(r!==a){a=ii(Error(i(424)),t),ji(a),t=cc(e,t,r,n);break a}switch(e=t.stateNode.containerInfo,e.nodeType){case 9:e=e.body;break;default:e=e.nodeName===`HTML`?e.ownerDocument.body:e}for(bi=cf(e.firstChild),yi=t,xi=!0,Si=null,Ci=!0,n=Ea(t,null,r,n),t.child=n;n;)n.flags=n.flags&-3|4096,n=n.sibling}else{if(ki(),r===a){t=yc(e,t,n);break a}Js(e,t,r,n)}t=t.child}return t;case 26:return ic(e,t),e===null?(n=kf(t.type,null,t.pendingProps,null))?t.memoizedState=n:xi||(n=t.type,e=t.pendingProps,r=Bd(te.current).createElement(n),r[Ze]=t,r[Qe]=e,Pd(r,n,e),ut(r),t.stateNode=r):t.memoizedState=kf(t.type,e.memoizedProps,t.pendingProps,e.memoizedState),null;case 27:return ie(t),e===null&&xi&&(r=t.stateNode=ff(t.type,t.pendingProps,te.current),yi=t,Ci=!0,a=bi,Zd(t.type)?(lf=a,bi=cf(r.firstChild)):bi=a),Js(e,t,t.pendingProps.children,n),ic(e,t),e===null&&(t.flags|=4194304),t.child;case 5:return e===null&&xi&&((a=r=bi)&&(r=tf(r,t.type,t.pendingProps,Ci),r===null?a=!1:(t.stateNode=r,yi=t,bi=cf(r.firstChild),Ci=!1,a=!0)),a||Ti(t)),ie(t),a=t.type,o=t.pendingProps,s=e===null?null:e.memoizedProps,r=o.children,Ud(a,o)?r=null:s!==null&&Ud(a,s)&&(t.flags|=32),t.memoizedState!==null&&(a=fo(e,t,ho,null,null,n),Qf._currentValue=a),ic(e,t),Js(e,t,r,n),t.child;case 6:return e===null&&xi&&((e=n=bi)&&(n=nf(n,t.pendingProps,Ci),n===null?e=!1:(t.stateNode=n,yi=t,bi=null,e=!0)),e||Ti(t)),null;case 13:return fc(e,t,n);case 4:return ne(t,t.stateNode.containerInfo),r=t.pendingProps,e===null?t.child=Ta(t,null,r,n):Js(e,t,r,n),t.child;case 11:return Ys(e,t,t.type,t.pendingProps,n);case 7:return Js(e,t,t.pendingProps,n),t.child;case 8:return Js(e,t,t.pendingProps.children,n),t.child;case 12:return Js(e,t,t.pendingProps.children,n),t.child;case 10:return r=t.pendingProps,Fi(t,t.type,r.value),Js(e,t,r.children,n),t.child;case 9:return a=t.type._context,r=t.pendingProps.children,Vi(t),a=Hi(a),r=r(a),t.flags|=1,Js(e,t,r,n),t.child;case 14:return Xs(e,t,t.type,t.pendingProps,n);case 15:return Zs(e,t,t.type,t.pendingProps,n);case 19:return vc(e,t,n);case 31:return rc(e,t,n);case 22:return Qs(e,t,n,t.pendingProps);case 24:return Vi(t),r=Hi(Ji),e===null?(a=oa(),a===null&&(a=Ml,o=Yi(),a.pooledCache=o,o.refCount++,o!==null&&(a.pooledCacheLanes|=n),a=o),t.memoizedState={parent:r,cache:a},Oa(t),Fi(t,Ji,a)):((e.lanes&n)!==0&&(ka(e,t),Ia(t,null,null,n),Fa()),a=e.memoizedState,o=t.memoizedState,a.parent===r?(r=o.cache,Fi(t,Ji,r),r!==a.cache&&Ri(t,[Ji],n,!0)):(a={parent:r,cache:r},t.memoizedState=a,t.lanes===0&&(t.memoizedState=t.updateQueue.baseState=a),Fi(t,Ji,r))),Js(e,t,t.pendingProps.children,n),t.child;case 29:throw t.pendingProps}throw Error(i(156,t.tag))}function Cc(e){e.flags|=4}function wc(e,t,n,r,i){if((t=!!(e.mode&32))&&(t=!1),t){if(e.flags|=16777216,(i&335544128)===i){if(e.stateNode.complete)e.flags|=8192;else if(xu())e.flags|=8192;else throw ga=fa,ua}}else e.flags&=-16777217}function Tc(e,t){if(t.type!==`stylesheet`||t.state.loading&4)e.flags&=-16777217;else if(e.flags|=16777216,!Wf(t)){if(xu())e.flags|=8192;else throw ga=fa,ua}}function Ec(e,t){t!==null&&(e.flags|=4),e.flags&16384&&(t=e.tag===22?536870912:ze(),e.lanes|=t,Kl|=t)}function Dc(e,t){if(!xi)switch(e.tailMode){case`hidden`:t=e.tail;for(var n=null;t!==null;)t.alternate!==null&&(n=t),t=t.sibling;n===null?e.tail=null:n.sibling=null;break;case`collapsed`:n=e.tail;for(var r=null;n!==null;)n.alternate!==null&&(r=n),n=n.sibling;r===null?t||e.tail===null?e.tail=null:e.tail.sibling=null:r.sibling=null}}function Oc(e){var t=e.alternate!==null&&e.alternate.child===e.child,n=0,r=0;if(t)for(var i=e.child;i!==null;)n|=i.lanes|i.childLanes,r|=i.subtreeFlags&65011712,r|=i.flags&65011712,i.return=e,i=i.sibling;else for(i=e.child;i!==null;)n|=i.lanes|i.childLanes,r|=i.subtreeFlags,r|=i.flags,i.return=e,i=i.sibling;return e.subtreeFlags|=r,e.childLanes=n,t}function kc(e,t,n){var r=t.pendingProps;switch(_i(t),t.tag){case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return Oc(t),null;case 1:return Oc(t),null;case 3:return n=t.stateNode,r=null,e!==null&&(r=e.memoizedState.cache),t.memoizedState.cache!==r&&(t.flags|=2048),Ii(Ji),re(),n.pendingContext&&(n.context=n.pendingContext,n.pendingContext=null),(e===null||e.child===null)&&(Oi(t)?Cc(t):e===null||e.memoizedState.isDehydrated&&!(t.flags&256)||(t.flags|=1024,Ai())),Oc(t),null;case 26:var a=t.type,o=t.memoizedState;return e===null?(Cc(t),o===null?(Oc(t),wc(t,a,null,r,n)):(Oc(t),Tc(t,o))):o?o===e.memoizedState?(Oc(t),t.flags&=-16777217):(Cc(t),Oc(t),Tc(t,o)):(e=e.memoizedProps,e!==r&&Cc(t),Oc(t),wc(t,a,e,r,n)),null;case 27:if(ae(t),n=te.current,a=t.type,e!==null&&t.stateNode!=null)e.memoizedProps!==r&&Cc(t);else{if(!r){if(t.stateNode===null)throw Error(i(166));return Oc(t),null}e=W.current,Oi(t)?Ei(t,e):(e=ff(a,r,n),t.stateNode=e,Cc(t))}return Oc(t),null;case 5:if(ae(t),a=t.type,e!==null&&t.stateNode!=null)e.memoizedProps!==r&&Cc(t);else{if(!r){if(t.stateNode===null)throw Error(i(166));return Oc(t),null}if(o=W.current,Oi(t))Ei(t,o);else{var s=Bd(te.current);switch(o){case 1:o=s.createElementNS(`http://www.w3.org/2000/svg`,a);break;case 2:o=s.createElementNS(`http://www.w3.org/1998/Math/MathML`,a);break;default:switch(a){case`svg`:o=s.createElementNS(`http://www.w3.org/2000/svg`,a);break;case`math`:o=s.createElementNS(`http://www.w3.org/1998/Math/MathML`,a);break;case`script`:o=s.createElement(`div`),o.innerHTML=`<script><\/script>`,o=o.removeChild(o.firstChild);break;case`select`:o=typeof r.is==`string`?s.createElement(`select`,{is:r.is}):s.createElement(`select`),r.multiple?o.multiple=!0:r.size&&(o.size=r.size);break;default:o=typeof r.is==`string`?s.createElement(a,{is:r.is}):s.createElement(a)}}o[Ze]=t,o[Qe]=r;a:for(s=t.child;s!==null;){if(s.tag===5||s.tag===6)o.appendChild(s.stateNode);else if(s.tag!==4&&s.tag!==27&&s.child!==null){s.child.return=s,s=s.child;continue}if(s===t)break a;for(;s.sibling===null;){if(s.return===null||s.return===t)break a;s=s.return}s.sibling.return=s.return,s=s.sibling}t.stateNode=o;a:switch(Pd(o,a,r),a){case`button`:case`input`:case`select`:case`textarea`:r=!!r.autoFocus;break a;case`img`:r=!0;break a;default:r=!1}r&&Cc(t)}}return Oc(t),wc(t,t.type,e===null?null:e.memoizedProps,t.pendingProps,n),null;case 6:if(e&&t.stateNode!=null)e.memoizedProps!==r&&Cc(t);else{if(typeof r!=`string`&&t.stateNode===null)throw Error(i(166));if(e=te.current,Oi(t)){if(e=t.stateNode,n=t.memoizedProps,r=null,a=yi,a!==null)switch(a.tag){case 27:case 5:r=a.memoizedProps}e[Ze]=t,e=!!(e.nodeValue===n||r!==null&&!0===r.suppressHydrationWarning||jd(e.nodeValue,n)),e||Ti(t,!0)}else e=Bd(e).createTextNode(r),e[Ze]=t,t.stateNode=e}return Oc(t),null;case 31:if(n=t.memoizedState,e===null||e.memoizedState!==null){if(r=Oi(t),n!==null){if(e===null){if(!r)throw Error(i(318));if(e=t.memoizedState,e=e===null?null:e.dehydrated,!e)throw Error(i(557));e[Ze]=t}else ki(),!(t.flags&128)&&(t.memoizedState=null),t.flags|=4;Oc(t),e=!1}else n=Ai(),e!==null&&e.memoizedState!==null&&(e.memoizedState.hydrationErrors=n),e=!0;if(!e)return t.flags&256?(Xa(t),t):(Xa(t),null);if(t.flags&128)throw Error(i(558))}return Oc(t),null;case 13:if(r=t.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(a=Oi(t),r!==null&&r.dehydrated!==null){if(e===null){if(!a)throw Error(i(318));if(a=t.memoizedState,a=a===null?null:a.dehydrated,!a)throw Error(i(317));a[Ze]=t}else ki(),!(t.flags&128)&&(t.memoizedState=null),t.flags|=4;Oc(t),a=!1}else a=Ai(),e!==null&&e.memoizedState!==null&&(e.memoizedState.hydrationErrors=a),a=!0;if(!a)return t.flags&256?(Xa(t),t):(Xa(t),null)}return Xa(t),t.flags&128?(t.lanes=n,t):(n=r!==null,e=e!==null&&e.memoizedState!==null,n&&(r=t.child,a=null,r.alternate!==null&&r.alternate.memoizedState!==null&&r.alternate.memoizedState.cachePool!==null&&(a=r.alternate.memoizedState.cachePool.pool),o=null,r.memoizedState!==null&&r.memoizedState.cachePool!==null&&(o=r.memoizedState.cachePool.pool),o!==a&&(r.flags|=2048)),n!==e&&n&&(t.child.flags|=8192),Ec(t,t.updateQueue),Oc(t),null);case 4:return re(),e===null&&xd(t.stateNode.containerInfo),Oc(t),null;case 10:return Ii(t.type),Oc(t),null;case 19:if(H(Za),r=t.memoizedState,r===null)return Oc(t),null;if(a=!!(t.flags&128),o=r.rendering,o===null){if(a)Dc(r,!1);else{if(Vl!==0||e!==null&&e.flags&128)for(e=t.child;e!==null;){if(o=Qa(e),o!==null){for(t.flags|=128,Dc(r,!1),e=o.updateQueue,t.updateQueue=e,Ec(t,e),t.subtreeFlags=0,e=n,n=t.child;n!==null;)Qr(n,e),n=n.sibling;return U(Za,Za.current&1|2),xi&&mi(t,r.treeForkCount),t.child}e=e.sibling}r.tail!==null&&ve()>Ql&&(t.flags|=128,a=!0,Dc(r,!1),t.lanes=4194304)}}else{if(!a){if(e=Qa(o),e!==null){if(t.flags|=128,a=!0,e=e.updateQueue,t.updateQueue=e,Ec(t,e),Dc(r,!0),r.tail===null&&r.tailMode===`hidden`&&!o.alternate&&!xi)return Oc(t),null}else 2*ve()-r.renderingStartTime>Ql&&n!==536870912&&(t.flags|=128,a=!0,Dc(r,!1),t.lanes=4194304)}r.isBackwards?(o.sibling=t.child,t.child=o):(e=r.last,e===null?t.child=o:e.sibling=o,r.last=o)}return r.tail===null?(Oc(t),null):(e=r.tail,r.rendering=e,r.tail=e.sibling,r.renderingStartTime=ve(),e.sibling=null,n=Za.current,U(Za,a?n&1|2:n&1),xi&&mi(t,r.treeForkCount),e);case 22:case 23:return Xa(t),Ua(),r=t.memoizedState!==null,e===null?r&&(t.flags|=8192):e.memoizedState!==null!==r&&(t.flags|=8192),r?n&536870912&&!(t.flags&128)&&(Oc(t),t.subtreeFlags&6&&(t.flags|=8192)):Oc(t),n=t.updateQueue,n!==null&&Ec(t,n.retryQueue),n=null,e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(n=e.memoizedState.cachePool.pool),r=null,t.memoizedState!==null&&t.memoizedState.cachePool!==null&&(r=t.memoizedState.cachePool.pool),r!==n&&(t.flags|=2048),e!==null&&H(aa),null;case 24:return n=null,e!==null&&(n=e.memoizedState.cache),t.memoizedState.cache!==n&&(t.flags|=2048),Ii(Ji),Oc(t),null;case 25:return null;case 30:return null}throw Error(i(156,t.tag))}function Ac(e,t){switch(_i(t),t.tag){case 1:return e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 3:return Ii(Ji),re(),e=t.flags,e&65536&&!(e&128)?(t.flags=e&-65537|128,t):null;case 26:case 27:case 5:return ae(t),null;case 31:if(t.memoizedState!==null){if(Xa(t),t.alternate===null)throw Error(i(340));ki()}return e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 13:if(Xa(t),e=t.memoizedState,e!==null&&e.dehydrated!==null){if(t.alternate===null)throw Error(i(340));ki()}return e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 19:return H(Za),null;case 4:return re(),null;case 10:return Ii(t.type),null;case 22:case 23:return Xa(t),Ua(),e!==null&&H(aa),e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 24:return Ii(Ji),null;case 25:return null;default:return null}}function jc(e,t){switch(_i(t),t.tag){case 3:Ii(Ji),re();break;case 26:case 27:case 5:ae(t);break;case 4:re();break;case 31:t.memoizedState!==null&&Xa(t);break;case 13:Xa(t);break;case 19:H(Za);break;case 10:Ii(t.type);break;case 22:case 23:Xa(t),Ua(),e!==null&&H(aa);break;case 24:Ii(Ji)}}function Mc(e,t){try{var n=t.updateQueue,r=n===null?null:n.lastEffect;if(r!==null){var i=r.next;n=i;do{if((n.tag&e)===e){r=void 0;var a=n.create,o=n.inst;r=a(),o.destroy=r}n=n.next}while(n!==i)}}catch(e){Hu(t,t.return,e)}}function Nc(e,t,n){try{var r=t.updateQueue,i=r===null?null:r.lastEffect;if(i!==null){var a=i.next;r=a;do{if((r.tag&e)===e){var o=r.inst,s=o.destroy;if(s!==void 0){o.destroy=void 0,i=t;var c=n,l=s;try{l()}catch(e){Hu(i,c,e)}}}r=r.next}while(r!==a)}}catch(e){Hu(t,t.return,e)}}function Pc(e){var t=e.updateQueue;if(t!==null){var n=e.stateNode;try{Ra(t,n)}catch(t){Hu(e,e.return,t)}}}function Fc(e,t,n){n.props=Is(e.type,e.memoizedProps),n.state=e.memoizedState;try{n.componentWillUnmount()}catch(n){Hu(e,t,n)}}function Ic(e,t){try{var n=e.ref;if(n!==null){switch(e.tag){case 26:case 27:case 5:var r=e.stateNode;break;case 30:r=e.stateNode;break;default:r=e.stateNode}typeof n==`function`?e.refCleanup=n(r):n.current=r}}catch(n){Hu(e,t,n)}}function Lc(e,t){var n=e.ref,r=e.refCleanup;if(n!==null){if(typeof r==`function`)try{r()}catch(n){Hu(e,t,n)}finally{e.refCleanup=null,e=e.alternate,e!=null&&(e.refCleanup=null)}else if(typeof n==`function`)try{n(null)}catch(n){Hu(e,t,n)}else n.current=null}}function Rc(e){var t=e.type,n=e.memoizedProps,r=e.stateNode;try{a:switch(t){case`button`:case`input`:case`select`:case`textarea`:n.autoFocus&&r.focus();break a;case`img`:n.src?r.src=n.src:n.srcSet&&(r.srcset=n.srcSet)}}catch(t){Hu(e,e.return,t)}}function zc(e,t,n){try{var r=e.stateNode;Fd(r,e.type,n,t),r[Qe]=t}catch(t){Hu(e,e.return,t)}}function Bc(e){return e.tag===5||e.tag===3||e.tag===26||e.tag===27&&Zd(e.type)||e.tag===4}function Vc(e){a:for(;;){for(;e.sibling===null;){if(e.return===null||Bc(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.tag===27&&Zd(e.type)||e.flags&2||e.child===null||e.tag===4)continue a;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function Hc(e,t,n){var r=e.tag;if(r===5||r===6)e=e.stateNode,t?(n.nodeType===9?n.body:n.nodeName===`HTML`?n.ownerDocument.body:n).insertBefore(e,t):(t=n.nodeType===9?n.body:n.nodeName===`HTML`?n.ownerDocument.body:n,t.appendChild(e),n=n._reactRootContainer,n!=null||t.onclick!==null||(t.onclick=Wt));else if(r!==4&&(r===27&&Zd(e.type)&&(n=e.stateNode,t=null),e=e.child,e!==null))for(Hc(e,t,n),e=e.sibling;e!==null;)Hc(e,t,n),e=e.sibling}function Uc(e,t,n){var r=e.tag;if(r===5||r===6)e=e.stateNode,t?n.insertBefore(e,t):n.appendChild(e);else if(r!==4&&(r===27&&Zd(e.type)&&(n=e.stateNode),e=e.child,e!==null))for(Uc(e,t,n),e=e.sibling;e!==null;)Uc(e,t,n),e=e.sibling}function Wc(e){var t=e.stateNode,n=e.memoizedProps;try{for(var r=e.type,i=t.attributes;i.length;)t.removeAttributeNode(i[0]);Pd(t,r,n),t[Ze]=e,t[Qe]=n}catch(t){Hu(e,e.return,t)}}var Gc=!1,Kc=!1,qc=!1,Jc=typeof WeakSet==`function`?WeakSet:Set,Yc=null;function Xc(e,t){if(e=e.containerInfo,Rd=sp,e=mr(e),hr(e)){if(`selectionStart`in e)var n={start:e.selectionStart,end:e.selectionEnd};else a:{n=(n=e.ownerDocument)&&n.defaultView||window;var r=n.getSelection&&n.getSelection();if(r&&r.rangeCount!==0){n=r.anchorNode;var a=r.anchorOffset,o=r.focusNode;r=r.focusOffset;try{n.nodeType,o.nodeType}catch{n=null;break a}var s=0,c=-1,l=-1,u=0,d=0,f=e,p=null;b:for(;;){for(var m;f!==n||a!==0&&f.nodeType!==3||(c=s+a),f!==o||r!==0&&f.nodeType!==3||(l=s+r),f.nodeType===3&&(s+=f.nodeValue.length),(m=f.firstChild)!==null;)p=f,f=m;for(;;){if(f===e)break b;if(p===n&&++u===a&&(c=s),p===o&&++d===r&&(l=s),(m=f.nextSibling)!==null)break;f=p,p=f.parentNode}f=m}n=c===-1||l===-1?null:{start:c,end:l}}else n=null}n||={start:0,end:0}}else n=null;for(zd={focusedElem:e,selectionRange:n},sp=!1,Yc=t;Yc!==null;)if(t=Yc,e=t.child,t.subtreeFlags&1028&&e!==null)e.return=t,Yc=e;else for(;Yc!==null;){switch(t=Yc,o=t.alternate,e=t.flags,t.tag){case 0:if(e&4&&(e=t.updateQueue,e=e===null?null:e.events,e!==null))for(n=0;n<e.length;n++)a=e[n],a.ref.impl=a.nextImpl;break;case 11:case 15:break;case 1:if(e&1024&&o!==null){e=void 0,n=t,a=o.memoizedProps,o=o.memoizedState,r=n.stateNode;try{var h=Is(n.type,a);e=r.getSnapshotBeforeUpdate(h,o),r.__reactInternalSnapshotBeforeUpdate=e}catch(e){Hu(n,n.return,e)}}break;case 3:if(e&1024){if(e=t.stateNode.containerInfo,n=e.nodeType,n===9)ef(e);else if(n===1)switch(e.nodeName){case`HEAD`:case`HTML`:case`BODY`:ef(e);break;default:e.textContent=``}}break;case 5:case 26:case 27:case 6:case 4:case 17:break;default:if(e&1024)throw Error(i(163))}if(e=t.sibling,e!==null){e.return=t.return,Yc=e;break}Yc=t.return}}function Zc(e,t,n){var r=n.flags;switch(n.tag){case 0:case 11:case 15:fl(e,n),r&4&&Mc(5,n);break;case 1:if(fl(e,n),r&4){if(e=n.stateNode,t===null)try{e.componentDidMount()}catch(e){Hu(n,n.return,e)}else{var i=Is(n.type,t.memoizedProps);t=t.memoizedState;try{e.componentDidUpdate(i,t,e.__reactInternalSnapshotBeforeUpdate)}catch(e){Hu(n,n.return,e)}}}r&64&&Pc(n),r&512&&Ic(n,n.return);break;case 3:if(fl(e,n),r&64&&(e=n.updateQueue,e!==null)){if(t=null,n.child!==null)switch(n.child.tag){case 27:case 5:t=n.child.stateNode;break;case 1:t=n.child.stateNode}try{Ra(e,t)}catch(e){Hu(n,n.return,e)}}break;case 27:t===null&&r&4&&Wc(n);case 26:case 5:fl(e,n),t===null&&r&4&&Rc(n),r&512&&Ic(n,n.return);break;case 12:fl(e,n);break;case 31:fl(e,n),r&4&&rl(e,n);break;case 13:fl(e,n),r&4&&il(e,n),r&64&&(e=n.memoizedState,e!==null&&(e=e.dehydrated,e!==null&&(n=Ku.bind(null,n),sf(e,n))));break;case 22:if(r=n.memoizedState!==null||Gc,!r){t=t!==null&&t.memoizedState!==null||Kc,i=Gc;var a=Kc;Gc=r,(Kc=t)&&!a?ml(e,n,!!(n.subtreeFlags&8772)):fl(e,n),Gc=i,Kc=a}break;case 30:break;default:fl(e,n)}}function Qc(e){var t=e.alternate;t!==null&&(e.alternate=null,Qc(t)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(t=e.stateNode,t!==null&&at(t)),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}var $c=null,el=!1;function tl(e,t,n){for(n=n.child;n!==null;)nl(e,t,n),n=n.sibling}function nl(e,t,n){if(Ee&&typeof Ee.onCommitFiberUnmount==`function`)try{Ee.onCommitFiberUnmount(Te,n)}catch{}switch(n.tag){case 26:Kc||Lc(n,t),tl(e,t,n),n.memoizedState?n.memoizedState.count--:n.stateNode&&(n=n.stateNode,n.parentNode.removeChild(n));break;case 27:Kc||Lc(n,t);var r=$c,i=el;Zd(n.type)&&($c=n.stateNode,el=!1),tl(e,t,n),pf(n.stateNode),$c=r,el=i;break;case 5:Kc||Lc(n,t);case 6:if(r=$c,i=el,$c=null,tl(e,t,n),$c=r,el=i,$c!==null){if(el)try{($c.nodeType===9?$c.body:$c.nodeName===`HTML`?$c.ownerDocument.body:$c).removeChild(n.stateNode)}catch(e){Hu(n,t,e)}else try{$c.removeChild(n.stateNode)}catch(e){Hu(n,t,e)}}break;case 18:$c!==null&&(el?(e=$c,Qd(e.nodeType===9?e.body:e.nodeName===`HTML`?e.ownerDocument.body:e,n.stateNode),Np(e)):Qd($c,n.stateNode));break;case 4:r=$c,i=el,$c=n.stateNode.containerInfo,el=!0,tl(e,t,n),$c=r,el=i;break;case 0:case 11:case 14:case 15:Nc(2,n,t),Kc||Nc(4,n,t),tl(e,t,n);break;case 1:Kc||(Lc(n,t),r=n.stateNode,typeof r.componentWillUnmount==`function`&&Fc(n,t,r)),tl(e,t,n);break;case 21:tl(e,t,n);break;case 22:Kc=(r=Kc)||n.memoizedState!==null,tl(e,t,n),Kc=r;break;default:tl(e,t,n)}}function rl(e,t){if(t.memoizedState===null&&(e=t.alternate,e!==null&&(e=e.memoizedState,e!==null))){e=e.dehydrated;try{Np(e)}catch(e){Hu(t,t.return,e)}}}function il(e,t){if(t.memoizedState===null&&(e=t.alternate,e!==null&&(e=e.memoizedState,e!==null&&(e=e.dehydrated,e!==null))))try{Np(e)}catch(e){Hu(t,t.return,e)}}function al(e){switch(e.tag){case 31:case 13:case 19:var t=e.stateNode;return t===null&&(t=e.stateNode=new Jc),t;case 22:return e=e.stateNode,t=e._retryCache,t===null&&(t=e._retryCache=new Jc),t;default:throw Error(i(435,e.tag))}}function ol(e,t){var n=al(e);t.forEach(function(t){if(!n.has(t)){n.add(t);var r=qu.bind(null,e,t);t.then(r,r)}})}function sl(e,t){var n=t.deletions;if(n!==null)for(var r=0;r<n.length;r++){var a=n[r],o=e,s=t,c=s;a:for(;c!==null;){switch(c.tag){case 27:if(Zd(c.type)){$c=c.stateNode,el=!1;break a}break;case 5:$c=c.stateNode,el=!1;break a;case 3:case 4:$c=c.stateNode.containerInfo,el=!0;break a}c=c.return}if($c===null)throw Error(i(160));nl(o,s,a),$c=null,el=!1,o=a.alternate,o!==null&&(o.return=null),a.return=null}if(t.subtreeFlags&13886)for(t=t.child;t!==null;)ll(t,e),t=t.sibling}var cl=null;function ll(e,t){var n=e.alternate,r=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:sl(t,e),ul(e),r&4&&(Nc(3,e,e.return),Mc(3,e),Nc(5,e,e.return));break;case 1:sl(t,e),ul(e),r&512&&(Kc||n===null||Lc(n,n.return)),r&64&&Gc&&(e=e.updateQueue,e!==null&&(r=e.callbacks,r!==null&&(n=e.shared.hiddenCallbacks,e.shared.hiddenCallbacks=n===null?r:n.concat(r))));break;case 26:var a=cl;if(sl(t,e),ul(e),r&512&&(Kc||n===null||Lc(n,n.return)),r&4){var o=n===null?null:n.memoizedState;if(r=e.memoizedState,n===null){if(r===null){if(e.stateNode===null){a:{r=e.type,n=e.memoizedProps,a=a.ownerDocument||a;b:switch(r){case`title`:o=a.getElementsByTagName(`title`)[0],(!o||o[it]||o[Ze]||o.namespaceURI===`http://www.w3.org/2000/svg`||o.hasAttribute(`itemprop`))&&(o=a.createElement(r),a.head.insertBefore(o,a.querySelector(`head > title`))),Pd(o,r,n),o[Ze]=e,ut(o),r=o;break a;case`link`:var s=Vf(`link`,`href`,a).get(r+(n.href||``));if(s){for(var c=0;c<s.length;c++)if(o=s[c],o.getAttribute(`href`)===(n.href==null||n.href===``?null:n.href)&&o.getAttribute(`rel`)===(n.rel==null?null:n.rel)&&o.getAttribute(`title`)===(n.title==null?null:n.title)&&o.getAttribute(`crossorigin`)===(n.crossOrigin==null?null:n.crossOrigin)){s.splice(c,1);break b}}o=a.createElement(r),Pd(o,r,n),a.head.appendChild(o);break;case`meta`:if(s=Vf(`meta`,`content`,a).get(r+(n.content||``))){for(c=0;c<s.length;c++)if(o=s[c],o.getAttribute(`content`)===(n.content==null?null:``+n.content)&&o.getAttribute(`name`)===(n.name==null?null:n.name)&&o.getAttribute(`property`)===(n.property==null?null:n.property)&&o.getAttribute(`http-equiv`)===(n.httpEquiv==null?null:n.httpEquiv)&&o.getAttribute(`charset`)===(n.charSet==null?null:n.charSet)){s.splice(c,1);break b}}o=a.createElement(r),Pd(o,r,n),a.head.appendChild(o);break;default:throw Error(i(468,r))}o[Ze]=e,ut(o),r=o}e.stateNode=r}else Hf(a,e.type,e.stateNode)}else e.stateNode=If(a,r,e.memoizedProps)}else o===r?r===null&&e.stateNode!==null&&zc(e,e.memoizedProps,n.memoizedProps):(o===null?n.stateNode!==null&&(n=n.stateNode,n.parentNode.removeChild(n)):o.count--,r===null?Hf(a,e.type,e.stateNode):If(a,r,e.memoizedProps))}break;case 27:sl(t,e),ul(e),r&512&&(Kc||n===null||Lc(n,n.return)),n!==null&&r&4&&zc(e,e.memoizedProps,n.memoizedProps);break;case 5:if(sl(t,e),ul(e),r&512&&(Kc||n===null||Lc(n,n.return)),e.flags&32){a=e.stateNode;try{It(a,``)}catch(t){Hu(e,e.return,t)}}r&4&&e.stateNode!=null&&(a=e.memoizedProps,zc(e,a,n===null?a:n.memoizedProps)),r&1024&&(qc=!0);break;case 6:if(sl(t,e),ul(e),r&4){if(e.stateNode===null)throw Error(i(162));r=e.memoizedProps,n=e.stateNode;try{n.nodeValue=r}catch(t){Hu(e,e.return,t)}}break;case 3:if(Bf=null,a=cl,cl=gf(t.containerInfo),sl(t,e),cl=a,ul(e),r&4&&n!==null&&n.memoizedState.isDehydrated)try{Np(t.containerInfo)}catch(t){Hu(e,e.return,t)}qc&&(qc=!1,dl(e));break;case 4:r=cl,cl=gf(e.stateNode.containerInfo),sl(t,e),ul(e),cl=r;break;case 12:sl(t,e),ul(e);break;case 31:sl(t,e),ul(e),r&4&&(r=e.updateQueue,r!==null&&(e.updateQueue=null,ol(e,r)));break;case 13:sl(t,e),ul(e),e.child.flags&8192&&e.memoizedState!==null!=(n!==null&&n.memoizedState!==null)&&(Xl=ve()),r&4&&(r=e.updateQueue,r!==null&&(e.updateQueue=null,ol(e,r)));break;case 22:a=e.memoizedState!==null;var l=n!==null&&n.memoizedState!==null,u=Gc,d=Kc;if(Gc=u||a,Kc=d||l,sl(t,e),Kc=d,Gc=u,ul(e),r&8192)a:for(t=e.stateNode,t._visibility=a?t._visibility&-2:t._visibility|1,a&&(n===null||l||Gc||Kc||pl(e)),n=null,t=e;;){if(t.tag===5||t.tag===26){if(n===null){l=n=t;try{if(o=l.stateNode,a)s=o.style,typeof s.setProperty==`function`?s.setProperty(`display`,`none`,`important`):s.display=`none`;else{c=l.stateNode;var f=l.memoizedProps.style,p=f!=null&&f.hasOwnProperty(`display`)?f.display:null;c.style.display=p==null||typeof p==`boolean`?``:(``+p).trim()}}catch(e){Hu(l,l.return,e)}}}else if(t.tag===6){if(n===null){l=t;try{l.stateNode.nodeValue=a?``:l.memoizedProps}catch(e){Hu(l,l.return,e)}}}else if(t.tag===18){if(n===null){l=t;try{var m=l.stateNode;a?$d(m,!0):$d(l.stateNode,!1)}catch(e){Hu(l,l.return,e)}}}else if((t.tag!==22&&t.tag!==23||t.memoizedState===null||t===e)&&t.child!==null){t.child.return=t,t=t.child;continue}if(t===e)break a;for(;t.sibling===null;){if(t.return===null||t.return===e)break a;n===t&&(n=null),t=t.return}n===t&&(n=null),t.sibling.return=t.return,t=t.sibling}r&4&&(r=e.updateQueue,r!==null&&(n=r.retryQueue,n!==null&&(r.retryQueue=null,ol(e,n))));break;case 19:sl(t,e),ul(e),r&4&&(r=e.updateQueue,r!==null&&(e.updateQueue=null,ol(e,r)));break;case 30:break;case 21:break;default:sl(t,e),ul(e)}}function ul(e){var t=e.flags;if(t&2){try{for(var n,r=e.return;r!==null;){if(Bc(r)){n=r;break}r=r.return}if(n==null)throw Error(i(160));switch(n.tag){case 27:var a=n.stateNode;Uc(e,Vc(e),a);break;case 5:var o=n.stateNode;n.flags&32&&(It(o,``),n.flags&=-33),Uc(e,Vc(e),o);break;case 3:case 4:var s=n.stateNode.containerInfo;Hc(e,Vc(e),s);break;default:throw Error(i(161))}}catch(t){Hu(e,e.return,t)}e.flags&=-3}t&4096&&(e.flags&=-4097)}function dl(e){if(e.subtreeFlags&1024)for(e=e.child;e!==null;){var t=e;dl(t),t.tag===5&&t.flags&1024&&t.stateNode.reset(),e=e.sibling}}function fl(e,t){if(t.subtreeFlags&8772)for(t=t.child;t!==null;)Zc(e,t.alternate,t),t=t.sibling}function pl(e){for(e=e.child;e!==null;){var t=e;switch(t.tag){case 0:case 11:case 14:case 15:Nc(4,t,t.return),pl(t);break;case 1:Lc(t,t.return);var n=t.stateNode;typeof n.componentWillUnmount==`function`&&Fc(t,t.return,n),pl(t);break;case 27:pf(t.stateNode);case 26:case 5:Lc(t,t.return),pl(t);break;case 22:t.memoizedState===null&&pl(t);break;case 30:pl(t);break;default:pl(t)}e=e.sibling}}function ml(e,t,n){for(n&&=!!(t.subtreeFlags&8772),t=t.child;t!==null;){var r=t.alternate,i=e,a=t,o=a.flags;switch(a.tag){case 0:case 11:case 15:ml(i,a,n),Mc(4,a);break;case 1:if(ml(i,a,n),r=a,i=r.stateNode,typeof i.componentDidMount==`function`)try{i.componentDidMount()}catch(e){Hu(r,r.return,e)}if(r=a,i=r.updateQueue,i!==null){var s=r.stateNode;try{var c=i.shared.hiddenCallbacks;if(c!==null)for(i.shared.hiddenCallbacks=null,i=0;i<c.length;i++)La(c[i],s)}catch(e){Hu(r,r.return,e)}}n&&o&64&&Pc(a),Ic(a,a.return);break;case 27:Wc(a);case 26:case 5:ml(i,a,n),n&&r===null&&o&4&&Rc(a),Ic(a,a.return);break;case 12:ml(i,a,n);break;case 31:ml(i,a,n),n&&o&4&&rl(i,a);break;case 13:ml(i,a,n),n&&o&4&&il(i,a);break;case 22:a.memoizedState===null&&ml(i,a,n),Ic(a,a.return);break;case 30:break;default:ml(i,a,n)}t=t.sibling}}function hl(e,t){var n=null;e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(n=e.memoizedState.cachePool.pool),e=null,t.memoizedState!==null&&t.memoizedState.cachePool!==null&&(e=t.memoizedState.cachePool.pool),e!==n&&(e!=null&&e.refCount++,n!=null&&Xi(n))}function gl(e,t){e=null,t.alternate!==null&&(e=t.alternate.memoizedState.cache),t=t.memoizedState.cache,t!==e&&(t.refCount++,e!=null&&Xi(e))}function _l(e,t,n,r){if(t.subtreeFlags&10256)for(t=t.child;t!==null;)vl(e,t,n,r),t=t.sibling}function vl(e,t,n,r){var i=t.flags;switch(t.tag){case 0:case 11:case 15:_l(e,t,n,r),i&2048&&Mc(9,t);break;case 1:_l(e,t,n,r);break;case 3:_l(e,t,n,r),i&2048&&(e=null,t.alternate!==null&&(e=t.alternate.memoizedState.cache),t=t.memoizedState.cache,t!==e&&(t.refCount++,e!=null&&Xi(e)));break;case 12:if(i&2048){_l(e,t,n,r),e=t.stateNode;try{var a=t.memoizedProps,o=a.id,s=a.onPostCommit;typeof s==`function`&&s(o,t.alternate===null?`mount`:`update`,e.passiveEffectDuration,-0)}catch(e){Hu(t,t.return,e)}}else _l(e,t,n,r);break;case 31:_l(e,t,n,r);break;case 13:_l(e,t,n,r);break;case 23:break;case 22:a=t.stateNode,o=t.alternate,t.memoizedState===null?a._visibility&2?_l(e,t,n,r):(a._visibility|=2,yl(e,t,n,r,!!(t.subtreeFlags&10256)||!1)):a._visibility&2?_l(e,t,n,r):bl(e,t),i&2048&&hl(o,t);break;case 24:_l(e,t,n,r),i&2048&&gl(t.alternate,t);break;default:_l(e,t,n,r)}}function yl(e,t,n,r,i){for(i&&=!!(t.subtreeFlags&10256)||!1,t=t.child;t!==null;){var a=e,o=t,s=n,c=r,l=o.flags;switch(o.tag){case 0:case 11:case 15:yl(a,o,s,c,i),Mc(8,o);break;case 23:break;case 22:var u=o.stateNode;o.memoizedState===null?(u._visibility|=2,yl(a,o,s,c,i)):u._visibility&2?yl(a,o,s,c,i):bl(a,o),i&&l&2048&&hl(o.alternate,o);break;case 24:yl(a,o,s,c,i),i&&l&2048&&gl(o.alternate,o);break;default:yl(a,o,s,c,i)}t=t.sibling}}function bl(e,t){if(t.subtreeFlags&10256)for(t=t.child;t!==null;){var n=e,r=t,i=r.flags;switch(r.tag){case 22:bl(n,r),i&2048&&hl(r.alternate,r);break;case 24:bl(n,r),i&2048&&gl(r.alternate,r);break;default:bl(n,r)}t=t.sibling}}var xl=8192;function Sl(e,t,n){if(e.subtreeFlags&xl)for(e=e.child;e!==null;)Cl(e,t,n),e=e.sibling}function Cl(e,t,n){switch(e.tag){case 26:Sl(e,t,n),e.flags&xl&&e.memoizedState!==null&&Gf(n,cl,e.memoizedState,e.memoizedProps);break;case 5:Sl(e,t,n);break;case 3:case 4:var r=cl;cl=gf(e.stateNode.containerInfo),Sl(e,t,n),cl=r;break;case 22:e.memoizedState===null&&(r=e.alternate,r!==null&&r.memoizedState!==null?(r=xl,xl=16777216,Sl(e,t,n),xl=r):Sl(e,t,n));break;default:Sl(e,t,n)}}function wl(e){var t=e.alternate;if(t!==null&&(e=t.child,e!==null)){t.child=null;do t=e.sibling,e.sibling=null,e=t;while(e!==null)}}function Tl(e){var t=e.deletions;if(e.flags&16){if(t!==null)for(var n=0;n<t.length;n++){var r=t[n];Yc=r,Ol(r,e)}wl(e)}if(e.subtreeFlags&10256)for(e=e.child;e!==null;)El(e),e=e.sibling}function El(e){switch(e.tag){case 0:case 11:case 15:Tl(e),e.flags&2048&&Nc(9,e,e.return);break;case 3:Tl(e);break;case 12:Tl(e);break;case 22:var t=e.stateNode;e.memoizedState!==null&&t._visibility&2&&(e.return===null||e.return.tag!==13)?(t._visibility&=-3,Dl(e)):Tl(e);break;default:Tl(e)}}function Dl(e){var t=e.deletions;if(e.flags&16){if(t!==null)for(var n=0;n<t.length;n++){var r=t[n];Yc=r,Ol(r,e)}wl(e)}for(e=e.child;e!==null;){switch(t=e,t.tag){case 0:case 11:case 15:Nc(8,t,t.return),Dl(t);break;case 22:n=t.stateNode,n._visibility&2&&(n._visibility&=-3,Dl(t));break;default:Dl(t)}e=e.sibling}}function Ol(e,t){for(;Yc!==null;){var n=Yc;switch(n.tag){case 0:case 11:case 15:Nc(8,n,t);break;case 23:case 22:if(n.memoizedState!==null&&n.memoizedState.cachePool!==null){var r=n.memoizedState.cachePool.pool;r!=null&&r.refCount++}break;case 24:Xi(n.memoizedState.cache)}if(r=n.child,r!==null)r.return=n,Yc=r;else a:for(n=e;Yc!==null;){r=Yc;var i=r.sibling,a=r.return;if(Qc(r),r===n){Yc=null;break a}if(i!==null){i.return=a,Yc=i;break a}Yc=a}}}var kl={getCacheForType:function(e){var t=Hi(Ji),n=t.data.get(e);return n===void 0&&(n=e(),t.data.set(e,n)),n},cacheSignal:function(){return Hi(Ji).controller.signal}},Al=typeof WeakMap==`function`?WeakMap:Map,jl=0,Ml=null,Nl=null,Pl=0,Fl=0,Il=null,Ll=!1,Rl=!1,zl=!1,Bl=0,Vl=0,Hl=0,Ul=0,Wl=0,Gl=0,Kl=0,ql=null,Jl=null,Yl=!1,Xl=0,Zl=0,Ql=1/0,$l=null,eu=null,tu=0,nu=null,ru=null,iu=0,au=0,ou=null,su=null,cu=0,lu=null;function uu(){return jl&2&&Pl!==0?Pl&-Pl:I.T===null?Je():ld()}function du(){if(Gl===0){if(!(Pl&536870912)||xi){var e=Ne;Ne<<=1,!(Ne&3932160)&&(Ne=262144),Gl=e}else Gl=536870912}return e=Wa.current,e!==null&&(e.flags|=32),Gl}function fu(e,t,n){(e===Ml&&(Fl===2||Fl===9)||e.cancelPendingCommit!==null)&&(yu(e,0),gu(e,Pl,Gl,!1)),Ve(e,n),(!(jl&2)||e!==Ml)&&(e===Ml&&(!(jl&2)&&(Ul|=n),Vl===4&&gu(e,Pl,Gl,!1)),td(e))}function pu(e,t,n){if(jl&6)throw Error(i(327));var r=!n&&!(t&127)&&(t&e.expiredLanes)===0||Le(e,t),a=r?Du(e,t):Tu(e,t,!0),o=r;do{if(a===0){Rl&&!r&&gu(e,t,0,!1);break}if(n=e.current.alternate,o&&!hu(n)){a=Tu(e,t,!1),o=!1;continue}if(a===2){if(o=t,e.errorRecoveryDisabledLanes&o)var s=0;else s=e.pendingLanes&-536870913,s=s===0?s&536870912?536870912:0:s;if(s!==0){t=s;a:{var c=e;a=ql;var l=c.current.memoizedState.isDehydrated;if(l&&(yu(c,s).flags|=256),s=Tu(c,s,!1),s!==2){if(zl&&!l){c.errorRecoveryDisabledLanes|=o,Ul|=o,a=4;break a}o=Jl,Jl=a,o!==null&&(Jl===null?Jl=o:Jl.push.apply(Jl,o))}a=s}if(o=!1,a!==2)continue}}if(a===1){yu(e,0),gu(e,t,0,!0);break}a:{switch(r=e,o=a,o){case 0:case 1:throw Error(i(345));case 4:if((t&4194048)!==t)break;case 6:gu(r,t,Gl,!Ll);break a;case 2:Jl=null;break;case 3:case 5:break;default:throw Error(i(329))}if((t&62914560)===t&&(a=Xl+300-ve(),10<a)){if(gu(r,t,Gl,!Ll),Ie(r,0,!0)!==0)break a;iu=t,r.timeoutHandle=Kd(mu.bind(null,r,n,Jl,$l,Yl,t,Gl,Ul,Kl,Ll,o,`Throttled`,-0,0),a);break a}mu(r,n,Jl,$l,Yl,t,Gl,Ul,Kl,Ll,o,null,-0,0)}break}while(1);td(e)}function mu(e,t,n,r,i,a,o,s,c,l,u,d,f,p){if(e.timeoutHandle=-1,d=t.subtreeFlags,d&8192||(d&16785408)==16785408){d={stylesheets:null,count:0,imgCount:0,imgBytes:0,suspenseyImages:[],waitingForImages:!0,waitingForViewTransition:!1,unsuspend:Wt},Cl(t,a,d);var m=(a&62914560)===a?Xl-ve():(a&4194048)===a?Zl-ve():0;if(m=qf(d,m),m!==null){iu=a,e.cancelPendingCommit=m(Pu.bind(null,e,t,a,n,r,i,o,s,c,u,d,null,f,p)),gu(e,a,o,!l);return}}Pu(e,t,a,n,r,i,o,s,c)}function hu(e){for(var t=e;;){var n=t.tag;if((n===0||n===11||n===15)&&t.flags&16384&&(n=t.updateQueue,n!==null&&(n=n.stores,n!==null)))for(var r=0;r<n.length;r++){var i=n[r],a=i.getSnapshot;i=i.value;try{if(!lr(a(),i))return!1}catch{return!1}}if(n=t.child,t.subtreeFlags&16384&&n!==null)n.return=t,t=n;else{if(t===e)break;for(;t.sibling===null;){if(t.return===null||t.return===e)return!0;t=t.return}t.sibling.return=t.return,t=t.sibling}}return!0}function gu(e,t,n,r){t&=~Wl,t&=~Ul,e.suspendedLanes|=t,e.pingedLanes&=~t,r&&(e.warmLanes|=t),r=e.expirationTimes;for(var i=t;0<i;){var a=31-Oe(i),o=1<<a;r[a]=-1,i&=~o}n!==0&&Ue(e,n,t)}function _u(){return jl&6?!0:(nd(0,!1),!1)}function vu(){if(Nl!==null){if(Fl===0)var e=Nl.return;else e=Nl,Pi=Ni=null,vo(e),ya=null,ba=0,e=Nl;for(;e!==null;)jc(e.alternate,e),e=e.return;Nl=null}}function yu(e,t){var n=e.timeoutHandle;n!==-1&&(e.timeoutHandle=-1,qd(n)),n=e.cancelPendingCommit,n!==null&&(e.cancelPendingCommit=null,n()),iu=0,vu(),Ml=e,Nl=n=Zr(e.current,null),Pl=t,Fl=0,Il=null,Ll=!1,Rl=Le(e,t),zl=!1,Kl=Gl=Wl=Ul=Hl=Vl=0,Jl=ql=null,Yl=!1,t&8&&(t|=t&32);var r=e.entangledLanes;if(r!==0)for(e=e.entanglements,r&=t;0<r;){var i=31-Oe(r),a=1<<i;t|=e[i],r&=~a}return Bl=t,Vr(),n}function bu(e,t){eo=null,I.H=Os,t===la||t===da?(t=_a(),Fl=3):t===ua?(t=_a(),Fl=4):Fl=t===Ks?8:typeof t==`object`&&t&&typeof t.then==`function`?6:1,Il=t,Nl===null&&(Vl=1,Bs(e,ii(t,e.current)))}function xu(){var e=Wa.current;return e===null?!0:(Pl&4194048)===Pl?Ga===null:(Pl&62914560)===Pl||Pl&536870912?e===Ga:!1}function Su(){var e=I.H;return I.H=Os,e===null?Os:e}function Cu(){var e=I.A;return I.A=kl,e}function wu(){Vl=4,Ll||(Pl&4194048)!==Pl&&Wa.current!==null||(Rl=!0),!(Hl&134217727)&&!(Ul&134217727)||Ml===null||gu(Ml,Pl,Gl,!1)}function Tu(e,t,n){var r=jl;jl|=2;var i=Su(),a=Cu();(Ml!==e||Pl!==t)&&($l=null,yu(e,t)),t=!1;var o=Vl;a:do try{if(Fl!==0&&Nl!==null){var s=Nl,c=Il;switch(Fl){case 8:vu(),o=6;break a;case 3:case 2:case 9:case 6:Wa.current===null&&(t=!0);var l=Fl;if(Fl=0,Il=null,ju(e,s,c,l),n&&Rl){o=0;break a}break;default:l=Fl,Fl=0,Il=null,ju(e,s,c,l)}}Eu(),o=Vl;break}catch(t){bu(e,t)}while(1);return t&&e.shellSuspendCounter++,Pi=Ni=null,jl=r,I.H=i,I.A=a,Nl===null&&(Ml=null,Pl=0,Vr()),o}function Eu(){for(;Nl!==null;)ku(Nl)}function Du(e,t){var n=jl;jl|=2;var r=Su(),a=Cu();Ml!==e||Pl!==t?($l=null,Ql=ve()+500,yu(e,t)):Rl=Le(e,t);a:do try{if(Fl!==0&&Nl!==null){t=Nl;var o=Il;b:switch(Fl){case 1:Fl=0,Il=null,ju(e,t,o,1);break;case 2:case 9:if(pa(o)){Fl=0,Il=null,Au(t);break}t=function(){Fl!==2&&Fl!==9||Ml!==e||(Fl=7),td(e)},o.then(t,t);break a;case 3:Fl=7;break a;case 4:Fl=5;break a;case 7:pa(o)?(Fl=0,Il=null,Au(t)):(Fl=0,Il=null,ju(e,t,o,7));break;case 5:var s=null;switch(Nl.tag){case 26:s=Nl.memoizedState;case 5:case 27:var c=Nl;if(s?Wf(s):c.stateNode.complete){Fl=0,Il=null;var l=c.sibling;if(l!==null)Nl=l;else{var u=c.return;u===null?Nl=null:(Nl=u,Mu(u))}break b}}Fl=0,Il=null,ju(e,t,o,5);break;case 6:Fl=0,Il=null,ju(e,t,o,6);break;case 8:vu(),Vl=6;break a;default:throw Error(i(462))}}Ou();break}catch(t){bu(e,t)}while(1);return Pi=Ni=null,I.H=r,I.A=a,jl=n,Nl===null?(Ml=null,Pl=0,Vr(),Vl):0}function Ou(){for(;Nl!==null&&!ge();)ku(Nl)}function ku(e){var t=Sc(e.alternate,e,Bl);e.memoizedProps=e.pendingProps,t===null?Mu(e):Nl=t}function Au(e){var t=e,n=t.alternate;switch(t.tag){case 15:case 0:t=oc(n,t,t.pendingProps,t.type,void 0,Pl);break;case 11:t=oc(n,t,t.pendingProps,t.type.render,t.ref,Pl);break;case 5:vo(t);default:jc(n,t),t=Nl=Qr(t,Bl),t=Sc(n,t,Bl)}e.memoizedProps=e.pendingProps,t===null?Mu(e):Nl=t}function ju(e,t,n,r){Pi=Ni=null,vo(t),ya=null,ba=0;var i=t.return;try{if(Gs(e,i,t,n,Pl)){Vl=1,Bs(e,ii(n,e.current)),Nl=null;return}}catch(t){if(i!==null)throw Nl=i,t;Vl=1,Bs(e,ii(n,e.current)),Nl=null;return}t.flags&32768?(xi||r===1?e=!0:Rl||Pl&536870912?e=!1:(Ll=e=!0,(r===2||r===9||r===3||r===6)&&(r=Wa.current,r!==null&&r.tag===13&&(r.flags|=16384))),Nu(t,e)):Mu(t)}function Mu(e){var t=e;do{if(t.flags&32768){Nu(t,Ll);return}e=t.return;var n=kc(t.alternate,t,Bl);if(n!==null){Nl=n;return}if(t=t.sibling,t!==null){Nl=t;return}Nl=t=e}while(t!==null);Vl===0&&(Vl=5)}function Nu(e,t){do{var n=Ac(e.alternate,e);if(n!==null){n.flags&=32767,Nl=n;return}if(n=e.return,n!==null&&(n.flags|=32768,n.subtreeFlags=0,n.deletions=null),!t&&(e=e.sibling,e!==null)){Nl=e;return}Nl=e=n}while(e!==null);Vl=6,Nl=null}function Pu(e,t,n,r,a,o,s,c,l){e.cancelPendingCommit=null;do zu();while(tu!==0);if(jl&6)throw Error(i(327));if(t!==null){if(t===e.current)throw Error(i(177));if(o=t.lanes|t.childLanes,o|=Br,He(e,n,o,s,c,l),e===Ml&&(Nl=Ml=null,Pl=0),ru=t,nu=e,iu=n,au=o,ou=a,su=r,t.subtreeFlags&10256||t.flags&10256?(e.callbackNode=null,e.callbackPriority=0,Ju(xe,function(){return Bu(),null})):(e.callbackNode=null,e.callbackPriority=0),r=!!(t.flags&13878),t.subtreeFlags&13878||r){r=I.T,I.T=null,a=L.p,L.p=2,s=jl,jl|=4;try{Xc(e,t,n)}finally{jl=s,L.p=a,I.T=r}}tu=1,Fu(),Iu(),Lu()}}function Fu(){if(tu===1){tu=0;var e=nu,t=ru,n=!!(t.flags&13878);if(t.subtreeFlags&13878||n){n=I.T,I.T=null;var r=L.p;L.p=2;var i=jl;jl|=4;try{ll(t,e);var a=zd,o=mr(e.containerInfo),s=a.focusedElem,c=a.selectionRange;if(o!==s&&s&&s.ownerDocument&&pr(s.ownerDocument.documentElement,s)){if(c!==null&&hr(s)){var l=c.start,u=c.end;if(u===void 0&&(u=l),`selectionStart`in s)s.selectionStart=l,s.selectionEnd=Math.min(u,s.value.length);else{var d=s.ownerDocument||document,f=d&&d.defaultView||window;if(f.getSelection){var p=f.getSelection(),m=s.textContent.length,h=Math.min(c.start,m),g=c.end===void 0?h:Math.min(c.end,m);!p.extend&&h>g&&(o=g,g=h,h=o);var _=fr(s,h),v=fr(s,g);if(_&&v&&(p.rangeCount!==1||p.anchorNode!==_.node||p.anchorOffset!==_.offset||p.focusNode!==v.node||p.focusOffset!==v.offset)){var y=d.createRange();y.setStart(_.node,_.offset),p.removeAllRanges(),h>g?(p.addRange(y),p.extend(v.node,v.offset)):(y.setEnd(v.node,v.offset),p.addRange(y))}}}}for(d=[],p=s;p=p.parentNode;)p.nodeType===1&&d.push({element:p,left:p.scrollLeft,top:p.scrollTop});for(typeof s.focus==`function`&&s.focus(),s=0;s<d.length;s++){var b=d[s];b.element.scrollLeft=b.left,b.element.scrollTop=b.top}}sp=!!Rd,zd=Rd=null}finally{jl=i,L.p=r,I.T=n}}e.current=t,tu=2}}function Iu(){if(tu===2){tu=0;var e=nu,t=ru,n=!!(t.flags&8772);if(t.subtreeFlags&8772||n){n=I.T,I.T=null;var r=L.p;L.p=2;var i=jl;jl|=4;try{Zc(e,t.alternate,t)}finally{jl=i,L.p=r,I.T=n}}tu=3}}function Lu(){if(tu===4||tu===3){tu=0,_e();var e=nu,t=ru,n=iu,r=su;t.subtreeFlags&10256||t.flags&10256?tu=5:(tu=0,ru=nu=null,Ru(e,e.pendingLanes));var i=e.pendingLanes;if(i===0&&(eu=null),qe(n),t=t.stateNode,Ee&&typeof Ee.onCommitFiberRoot==`function`)try{Ee.onCommitFiberRoot(Te,t,void 0,(t.current.flags&128)==128)}catch{}if(r!==null){t=I.T,i=L.p,L.p=2,I.T=null;try{for(var a=e.onRecoverableError,o=0;o<r.length;o++){var s=r[o];a(s.value,{componentStack:s.stack})}}finally{I.T=t,L.p=i}}iu&3&&zu(),td(e),i=e.pendingLanes,n&261930&&i&42?e===lu?cu++:(cu=0,lu=e):cu=0,nd(0,!1)}}function Ru(e,t){(e.pooledCacheLanes&=t)===0&&(t=e.pooledCache,t!=null&&(e.pooledCache=null,Xi(t)))}function zu(){return Fu(),Iu(),Lu(),Bu()}function Bu(){if(tu!==5)return!1;var e=nu,t=au;au=0;var n=qe(iu),r=I.T,a=L.p;try{L.p=32>n?32:n,I.T=null,n=ou,ou=null;var o=nu,s=iu;if(tu=0,ru=nu=null,iu=0,jl&6)throw Error(i(331));var c=jl;if(jl|=4,El(o.current),vl(o,o.current,s,n),jl=c,nd(0,!1),Ee&&typeof Ee.onPostCommitFiberRoot==`function`)try{Ee.onPostCommitFiberRoot(Te,o)}catch{}return!0}finally{L.p=a,I.T=r,Ru(e,t)}}function Vu(e,t,n){t=ii(n,t),t=Hs(e.stateNode,t,2),e=ja(e,t,2),e!==null&&(Ve(e,2),td(e))}function Hu(e,t,n){if(e.tag===3)Vu(e,e,n);else for(;t!==null;){if(t.tag===3){Vu(t,e,n);break}if(t.tag===1){var r=t.stateNode;if(typeof t.type.getDerivedStateFromError==`function`||typeof r.componentDidCatch==`function`&&(eu===null||!eu.has(r))){e=ii(n,e),n=Us(2),r=ja(t,n,2),r!==null&&(Ws(n,r,t,e),Ve(r,2),td(r));break}}t=t.return}}function Uu(e,t,n){var r=e.pingCache;if(r===null){r=e.pingCache=new Al;var i=new Set;r.set(t,i)}else i=r.get(t),i===void 0&&(i=new Set,r.set(t,i));i.has(n)||(zl=!0,i.add(n),e=Wu.bind(null,e,t,n),t.then(e,e))}function Wu(e,t,n){var r=e.pingCache;r!==null&&r.delete(t),e.pingedLanes|=e.suspendedLanes&n,e.warmLanes&=~n,Ml===e&&(Pl&n)===n&&(Vl===4||Vl===3&&(Pl&62914560)===Pl&&300>ve()-Xl?!(jl&2)&&yu(e,0):Wl|=n,Kl===Pl&&(Kl=0)),td(e)}function Gu(e,t){t===0&&(t=ze()),e=Wr(e,t),e!==null&&(Ve(e,t),td(e))}function Ku(e){var t=e.memoizedState,n=0;t!==null&&(n=t.retryLane),Gu(e,n)}function qu(e,t){var n=0;switch(e.tag){case 31:case 13:var r=e.stateNode,a=e.memoizedState;a!==null&&(n=a.retryLane);break;case 19:r=e.stateNode;break;case 22:r=e.stateNode._retryCache;break;default:throw Error(i(314))}r!==null&&r.delete(t),Gu(e,n)}function Ju(e,t){return me(e,t)}var Yu=null,Xu=null,Zu=!1,Qu=!1,$u=!1,ed=0;function td(e){e!==Xu&&e.next===null&&(Xu===null?Yu=Xu=e:Xu=Xu.next=e),Qu=!0,Zu||(Zu=!0,cd())}function nd(e,t){if(!$u&&Qu){$u=!0;do for(var n=!1,r=Yu;r!==null;){if(!t){if(e!==0){var i=r.pendingLanes;if(i===0)var a=0;else{var o=r.suspendedLanes,s=r.pingedLanes;a=(1<<31-Oe(42|e)+1)-1,a&=i&~(o&~s),a=a&201326741?a&201326741|1:a?a|2:0}a!==0&&(n=!0,sd(r,a))}else a=Pl,a=Ie(r,r===Ml?a:0,r.cancelPendingCommit!==null||r.timeoutHandle!==-1),!(a&3)||Le(r,a)||(n=!0,sd(r,a))}r=r.next}while(n);$u=!1}}function rd(){id()}function id(){Qu=Zu=!1;var e=0;ed!==0&&Gd()&&(e=ed);for(var t=ve(),n=null,r=Yu;r!==null;){var i=r.next,a=ad(r,t);a===0?(r.next=null,n===null?Yu=i:n.next=i,i===null&&(Xu=n)):(n=r,(e!==0||a&3)&&(Qu=!0)),r=i}tu!==0&&tu!==5||nd(e,!1),ed!==0&&(ed=0)}function ad(e,t){for(var n=e.suspendedLanes,r=e.pingedLanes,i=e.expirationTimes,a=e.pendingLanes&-62914561;0<a;){var o=31-Oe(a),s=1<<o,c=i[o];c===-1?((s&n)===0||(s&r)!==0)&&(i[o]=Re(s,t)):c<=t&&(e.expiredLanes|=s),a&=~s}if(t=Ml,n=Pl,n=Ie(e,e===t?n:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),r=e.callbackNode,n===0||e===t&&(Fl===2||Fl===9)||e.cancelPendingCommit!==null)return r!==null&&r!==null&&he(r),e.callbackNode=null,e.callbackPriority=0;if(!(n&3)||Le(e,n)){if(t=n&-n,t===e.callbackPriority)return t;switch(r!==null&&he(r),qe(n)){case 2:case 8:n=be;break;case 32:n=xe;break;case 268435456:n=Se;break;default:n=xe}return r=od.bind(null,e),n=me(n,r),e.callbackPriority=t,e.callbackNode=n,t}return r!==null&&r!==null&&he(r),e.callbackPriority=2,e.callbackNode=null,2}function od(e,t){if(tu!==0&&tu!==5)return e.callbackNode=null,e.callbackPriority=0,null;var n=e.callbackNode;if(zu()&&e.callbackNode!==n)return null;var r=Pl;return r=Ie(e,e===Ml?r:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),r===0?null:(pu(e,r,t),ad(e,ve()),e.callbackNode!=null&&e.callbackNode===n?od.bind(null,e):null)}function sd(e,t){if(zu())return null;pu(e,t,!0)}function cd(){Yd(function(){jl&6?me(K,rd):id()})}function ld(){if(ed===0){var e=$i;e===0&&(e=Me,Me<<=1,!(Me&261888)&&(Me=256)),ed=e}return ed}function ud(e){return e==null||typeof e==`symbol`||typeof e==`boolean`?null:typeof e==`function`?e:Ut(``+e)}function dd(e,t){var n=t.ownerDocument.createElement(`input`);return n.name=t.name,n.value=t.value,e.id&&n.setAttribute(`form`,e.id),t.parentNode.insertBefore(n,t),e=new FormData(e),n.parentNode.removeChild(n),e}function fd(e,t,n,r,i){if(t===`submit`&&n&&n.stateNode===i){var a=ud((i[Qe]||null).action),o=r.submitter;o&&(t=(t=o[Qe]||null)?ud(t.formAction):o.getAttribute(`formAction`),t!==null&&(a=t,o=null));var s=new fn(`action`,`action`,null,r,i);e.push({event:s,listeners:[{instance:null,listener:function(){if(r.defaultPrevented){if(ed!==0){var e=o?dd(i,o):new FormData(i);ms(n,{pending:!0,data:e,method:i.method,action:a},null,e)}}else typeof a==`function`&&(s.preventDefault(),e=o?dd(i,o):new FormData(i),ms(n,{pending:!0,data:e,method:i.method,action:a},a,e))},currentTarget:i}]})}}for(var pd=0;pd<Fr.length;pd++){var md=Fr[pd];Ir(md.toLowerCase(),`on`+(md[0].toUpperCase()+md.slice(1)))}Ir(Dr,`onAnimationEnd`),Ir(Or,`onAnimationIteration`),Ir(kr,`onAnimationStart`),Ir(`dblclick`,`onDoubleClick`),Ir(`focusin`,`onFocus`),Ir(`focusout`,`onBlur`),Ir(Ar,`onTransitionRun`),Ir(jr,`onTransitionStart`),Ir(Mr,`onTransitionCancel`),Ir(Nr,`onTransitionEnd`),mt(`onMouseEnter`,[`mouseout`,`mouseover`]),mt(`onMouseLeave`,[`mouseout`,`mouseover`]),mt(`onPointerEnter`,[`pointerout`,`pointerover`]),mt(`onPointerLeave`,[`pointerout`,`pointerover`]),pt(`onChange`,`change click focusin focusout input keydown keyup selectionchange`.split(` `)),pt(`onSelect`,`focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange`.split(` `)),pt(`onBeforeInput`,[`compositionend`,`keypress`,`textInput`,`paste`]),pt(`onCompositionEnd`,`compositionend focusout keydown keypress keyup mousedown`.split(` `)),pt(`onCompositionStart`,`compositionstart focusout keydown keypress keyup mousedown`.split(` `)),pt(`onCompositionUpdate`,`compositionupdate focusout keydown keypress keyup mousedown`.split(` `));var hd=`abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting`.split(` `),gd=new Set(`beforetoggle cancel close invalid load scroll scrollend toggle`.split(` `).concat(hd));function _d(e,t){t=!!(t&4);for(var n=0;n<e.length;n++){var r=e[n],i=r.event;r=r.listeners;a:{var a=void 0;if(t)for(var o=r.length-1;0<=o;o--){var s=r[o],c=s.instance,l=s.currentTarget;if(s=s.listener,c!==a&&i.isPropagationStopped())break a;a=s,i.currentTarget=l;try{a(i)}catch(e){Lr(e)}i.currentTarget=null,a=c}else for(o=0;o<r.length;o++){if(s=r[o],c=s.instance,l=s.currentTarget,s=s.listener,c!==a&&i.isPropagationStopped())break a;a=s,i.currentTarget=l;try{a(i)}catch(e){Lr(e)}i.currentTarget=null,a=c}}}}function vd(e,t){var n=t[et];n===void 0&&(n=t[et]=new Set);var r=e+`__bubble`;n.has(r)||(Sd(t,e,2,!1),n.add(r))}function yd(e,t,n){var r=0;t&&(r|=4),Sd(n,e,r,t)}var bd=`_reactListening`+Math.random().toString(36).slice(2);function xd(e){if(!e[bd]){e[bd]=!0,dt.forEach(function(t){t!==`selectionchange`&&(gd.has(t)||yd(t,!1,e),yd(t,!0,e))});var t=e.nodeType===9?e:e.ownerDocument;t===null||t[bd]||(t[bd]=!0,yd(`selectionchange`,!1,t))}}function Sd(e,t,n,r){switch(mp(t)){case 2:var i=cp;break;case 8:i=lp;break;default:i=up}n=i.bind(null,t,n,e),i=void 0,!en||t!==`touchstart`&&t!==`touchmove`&&t!==`wheel`||(i=!0),r?i===void 0?e.addEventListener(t,n,!0):e.addEventListener(t,n,{capture:!0,passive:i}):i===void 0?e.addEventListener(t,n,!1):e.addEventListener(t,n,{passive:i})}function Cd(e,t,n,r,i){var a=r;if(!(t&1)&&!(t&2)&&r!==null)a:for(;;){if(r===null)return;var s=r.tag;if(s===3||s===4){var c=r.stateNode.containerInfo;if(c===i)break;if(s===4)for(s=r.return;s!==null;){var l=s.tag;if((l===3||l===4)&&s.stateNode.containerInfo===i)return;s=s.return}for(;c!==null;){if(s=ot(c),s===null)return;if(l=s.tag,l===5||l===6||l===26||l===27){r=a=s;continue a}c=c.parentNode}}r=r.return}Zt(function(){var r=a,i=Kt(n),s=[];a:{var c=Pr.get(e);if(c!==void 0){var l=fn,u=e;switch(e){case`keypress`:if(sn(n)===0)break a;case`keydown`:case`keyup`:l=kn;break;case`focusin`:u=`focus`,l=xn;break;case`focusout`:u=`blur`,l=xn;break;case`beforeblur`:case`afterblur`:l=xn;break;case`click`:if(n.button===2)break a;case`auxclick`:case`dblclick`:case`mousedown`:case`mousemove`:case`mouseup`:case`mouseout`:case`mouseover`:case`contextmenu`:l=yn;break;case`drag`:case`dragend`:case`dragenter`:case`dragexit`:case`dragleave`:case`dragover`:case`dragstart`:case`drop`:l=bn;break;case`touchcancel`:case`touchend`:case`touchmove`:case`touchstart`:l=Y;break;case Dr:case Or:case kr:l=Sn;break;case Nr:l=jn;break;case`scroll`:case`scrollend`:l=mn;break;case`wheel`:l=Mn;break;case`copy`:case`cut`:case`paste`:l=Cn;break;case`gotpointercapture`:case`lostpointercapture`:case`pointercancel`:case`pointerdown`:case`pointermove`:case`pointerout`:case`pointerover`:case`pointerup`:l=An;break;case`toggle`:case`beforetoggle`:l=Nn}var d=!!(t&4),f=!d&&(e===`scroll`||e===`scrollend`),p=d?c===null?null:c+`Capture`:c;d=[];for(var m=r,h;m!==null;){var g=m;if(h=g.stateNode,g=g.tag,g!==5&&g!==26&&g!==27||h===null||p===null||(g=Qt(m,p),g!=null&&d.push(wd(m,g,h))),f)break;m=m.return}0<d.length&&(c=new l(c,u,null,n,i),s.push({event:c,listeners:d}))}}if(!(t&7)){a:{if(c=e===`mouseover`||e===`pointerover`,l=e===`mouseout`||e===`pointerout`,c&&n!==Gt&&(u=n.relatedTarget||n.fromElement)&&(ot(u)||u[$e]))break a;if((l||c)&&(c=i.window===i?i:(c=i.ownerDocument)?c.defaultView||c.parentWindow:window,l?(u=n.relatedTarget||n.toElement,l=r,u=u?ot(u):null,u!==null&&(f=o(u),d=u.tag,u!==f||d!==5&&d!==27&&d!==6)&&(u=null)):(l=null,u=r),l!==u)){if(d=yn,g=`onMouseLeave`,p=`onMouseEnter`,m=`mouse`,(e===`pointerout`||e===`pointerover`)&&(d=An,g=`onPointerLeave`,p=`onPointerEnter`,m=`pointer`),f=l==null?c:ct(l),h=u==null?c:ct(u),c=new d(g,m+`leave`,l,n,i),c.target=f,c.relatedTarget=h,g=null,ot(i)===r&&(d=new d(p,m+`enter`,u,n,i),d.target=h,d.relatedTarget=f,g=d),f=g,l&&u)b:{for(d=Ed,p=l,m=u,h=0,g=p;g;g=d(g))h++;g=0;for(var _=m;_;_=d(_))g++;for(;0<h-g;)p=d(p),h--;for(;0<g-h;)m=d(m),g--;for(;h--;){if(p===m||m!==null&&p===m.alternate){d=p;break b}p=d(p),m=d(m)}d=null}else d=null;l!==null&&Dd(s,c,l,d,!1),u!==null&&f!==null&&Dd(s,f,u,d,!0)}}a:{if(c=r?ct(r):window,l=c.nodeName&&c.nodeName.toLowerCase(),l===`select`||l===`input`&&c.type===`file`)var v=Zn;else if(qn(c)){if(Qn)v=sr;else{v=ar;var y=ir}}else l=c.nodeName,!l||l.toLowerCase()!==`input`||c.type!==`checkbox`&&c.type!==`radio`?r&&Bt(r.elementType)&&(v=Zn):v=or;if(v&&=v(e,r)){Jn(s,v,n,i);break a}y&&y(e,c,r),e===`focusout`&&r&&c.type===`number`&&r.memoizedProps.value!=null&&Mt(c,`number`,c.value)}switch(y=r?ct(r):window,e){case`focusin`:(qn(y)||y.contentEditable===`true`)&&(_r=y,vr=r,yr=null);break;case`focusout`:yr=vr=_r=null;break;case`mousedown`:br=!0;break;case`contextmenu`:case`mouseup`:case`dragend`:br=!1,xr(s,n,i);break;case`selectionchange`:if(gr)break;case`keydown`:case`keyup`:xr(s,n,i)}var b;if(Fn)b:{switch(e){case`compositionstart`:var x=`onCompositionStart`;break b;case`compositionend`:x=`onCompositionEnd`;break b;case`compositionupdate`:x=`onCompositionUpdate`;break b}x=void 0}else Un?Vn(e,n)&&(x=`onCompositionEnd`):e===`keydown`&&n.keyCode===229&&(x=`onCompositionStart`);x&&(Rn&&n.locale!==`ko`&&(Un||x!==`onCompositionStart`?x===`onCompositionEnd`&&Un&&(b=on()):(nn=i,rn=`value`in nn?nn.value:nn.textContent,Un=!0)),y=Td(r,x),0<y.length&&(x=new J(x,e,null,n,i),s.push({event:x,listeners:y}),b?x.data=b:(b=Hn(n),b!==null&&(x.data=b)))),(b=Ln?Wn(e,n):Gn(e,n))&&(x=Td(r,`onBeforeInput`),0<x.length&&(y=new J(`onBeforeInput`,`beforeinput`,null,n,i),s.push({event:y,listeners:x}),y.data=b)),fd(s,e,r,n,i)}_d(s,t)})}function wd(e,t,n){return{instance:e,listener:t,currentTarget:n}}function Td(e,t){for(var n=t+`Capture`,r=[];e!==null;){var i=e,a=i.stateNode;if(i=i.tag,i!==5&&i!==26&&i!==27||a===null||(i=Qt(e,n),i!=null&&r.unshift(wd(e,i,a)),i=Qt(e,t),i!=null&&r.push(wd(e,i,a))),e.tag===3)return r;e=e.return}return[]}function Ed(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5&&e.tag!==27);return e||null}function Dd(e,t,n,r,i){for(var a=t._reactName,o=[];n!==null&&n!==r;){var s=n,c=s.alternate,l=s.stateNode;if(s=s.tag,c!==null&&c===r)break;s!==5&&s!==26&&s!==27||l===null||(c=l,i?(l=Qt(n,a),l!=null&&o.unshift(wd(n,l,c))):i||(l=Qt(n,a),l!=null&&o.push(wd(n,l,c)))),n=n.return}o.length!==0&&e.push({event:t,listeners:o})}var Od=/\r\n?/g,kd=/\u0000|\uFFFD/g;function Ad(e){return(typeof e==`string`?e:``+e).replace(Od,`
`).replace(kd,``)}function jd(e,t){return t=Ad(t),Ad(e)===t}function Md(e,t,n,r,a,o){switch(n){case`children`:typeof r==`string`?t===`body`||t===`textarea`&&r===``||It(e,r):(typeof r==`number`||typeof r==`bigint`)&&t!==`body`&&It(e,``+r);break;case`className`:bt(e,`class`,r);break;case`tabIndex`:bt(e,`tabindex`,r);break;case`dir`:case`role`:case`viewBox`:case`width`:case`height`:bt(e,n,r);break;case`style`:zt(e,r,o);break;case`data`:if(t!==`object`){bt(e,`data`,r);break}case`src`:case`href`:if(r===``&&(t!==`a`||n!==`href`)){e.removeAttribute(n);break}if(r==null||typeof r==`function`||typeof r==`symbol`||typeof r==`boolean`){e.removeAttribute(n);break}r=Ut(``+r),e.setAttribute(n,r);break;case`action`:case`formAction`:if(typeof r==`function`){e.setAttribute(n,`javascript:throw new Error('A React form was unexpectedly submitted. If you called form.submit() manually, consider using form.requestSubmit() instead. If you\\'re trying to use event.stopPropagation() in a submit event handler, consider also calling event.preventDefault().')`);break}if(typeof o==`function`&&(n===`formAction`?(t!==`input`&&Md(e,t,`name`,a.name,a,null),Md(e,t,`formEncType`,a.formEncType,a,null),Md(e,t,`formMethod`,a.formMethod,a,null),Md(e,t,`formTarget`,a.formTarget,a,null)):(Md(e,t,`encType`,a.encType,a,null),Md(e,t,`method`,a.method,a,null),Md(e,t,`target`,a.target,a,null))),r==null||typeof r==`symbol`||typeof r==`boolean`){e.removeAttribute(n);break}r=Ut(``+r),e.setAttribute(n,r);break;case`onClick`:r!=null&&(e.onclick=Wt);break;case`onScroll`:r!=null&&vd(`scroll`,e);break;case`onScrollEnd`:r!=null&&vd(`scrollend`,e);break;case`dangerouslySetInnerHTML`:if(r!=null){if(typeof r!=`object`||!(`__html`in r))throw Error(i(61));if(n=r.__html,n!=null){if(a.children!=null)throw Error(i(60));e.innerHTML=n}}break;case`multiple`:e.multiple=r&&typeof r!=`function`&&typeof r!=`symbol`;break;case`muted`:e.muted=r&&typeof r!=`function`&&typeof r!=`symbol`;break;case`suppressContentEditableWarning`:case`suppressHydrationWarning`:case`defaultValue`:case`defaultChecked`:case`innerHTML`:case`ref`:break;case`autoFocus`:break;case`xlinkHref`:if(r==null||typeof r==`function`||typeof r==`boolean`||typeof r==`symbol`){e.removeAttribute(`xlink:href`);break}n=Ut(``+r),e.setAttributeNS(`http://www.w3.org/1999/xlink`,`xlink:href`,n);break;case`contentEditable`:case`spellCheck`:case`draggable`:case`value`:case`autoReverse`:case`externalResourcesRequired`:case`focusable`:case`preserveAlpha`:r!=null&&typeof r!=`function`&&typeof r!=`symbol`?e.setAttribute(n,``+r):e.removeAttribute(n);break;case`inert`:case`allowFullScreen`:case`async`:case`autoPlay`:case`controls`:case`default`:case`defer`:case`disabled`:case`disablePictureInPicture`:case`disableRemotePlayback`:case`formNoValidate`:case`hidden`:case`loop`:case`noModule`:case`noValidate`:case`open`:case`playsInline`:case`readOnly`:case`required`:case`reversed`:case`scoped`:case`seamless`:case`itemScope`:r&&typeof r!=`function`&&typeof r!=`symbol`?e.setAttribute(n,``):e.removeAttribute(n);break;case`capture`:case`download`:!0===r?e.setAttribute(n,``):!1!==r&&r!=null&&typeof r!=`function`&&typeof r!=`symbol`?e.setAttribute(n,r):e.removeAttribute(n);break;case`cols`:case`rows`:case`size`:case`span`:r!=null&&typeof r!=`function`&&typeof r!=`symbol`&&!isNaN(r)&&1<=r?e.setAttribute(n,r):e.removeAttribute(n);break;case`rowSpan`:case`start`:r==null||typeof r==`function`||typeof r==`symbol`||isNaN(r)?e.removeAttribute(n):e.setAttribute(n,r);break;case`popover`:vd(`beforetoggle`,e),vd(`toggle`,e),yt(e,`popover`,r);break;case`xlinkActuate`:xt(e,`http://www.w3.org/1999/xlink`,`xlink:actuate`,r);break;case`xlinkArcrole`:xt(e,`http://www.w3.org/1999/xlink`,`xlink:arcrole`,r);break;case`xlinkRole`:xt(e,`http://www.w3.org/1999/xlink`,`xlink:role`,r);break;case`xlinkShow`:xt(e,`http://www.w3.org/1999/xlink`,`xlink:show`,r);break;case`xlinkTitle`:xt(e,`http://www.w3.org/1999/xlink`,`xlink:title`,r);break;case`xlinkType`:xt(e,`http://www.w3.org/1999/xlink`,`xlink:type`,r);break;case`xmlBase`:xt(e,`http://www.w3.org/XML/1998/namespace`,`xml:base`,r);break;case`xmlLang`:xt(e,`http://www.w3.org/XML/1998/namespace`,`xml:lang`,r);break;case`xmlSpace`:xt(e,`http://www.w3.org/XML/1998/namespace`,`xml:space`,r);break;case`is`:yt(e,`is`,r);break;case`innerText`:case`textContent`:break;default:(!(2<n.length)||n[0]!==`o`&&n[0]!==`O`||n[1]!==`n`&&n[1]!==`N`)&&(n=Vt.get(n)||n,yt(e,n,r))}}function Nd(e,t,n,r,a,o){switch(n){case`style`:zt(e,r,o);break;case`dangerouslySetInnerHTML`:if(r!=null){if(typeof r!=`object`||!(`__html`in r))throw Error(i(61));if(n=r.__html,n!=null){if(a.children!=null)throw Error(i(60));e.innerHTML=n}}break;case`children`:typeof r==`string`?It(e,r):(typeof r==`number`||typeof r==`bigint`)&&It(e,``+r);break;case`onScroll`:r!=null&&vd(`scroll`,e);break;case`onScrollEnd`:r!=null&&vd(`scrollend`,e);break;case`onClick`:r!=null&&(e.onclick=Wt);break;case`suppressContentEditableWarning`:case`suppressHydrationWarning`:case`innerHTML`:case`ref`:break;case`innerText`:case`textContent`:break;default:if(!ft.hasOwnProperty(n))a:{if(n[0]===`o`&&n[1]===`n`&&(a=n.endsWith(`Capture`),t=n.slice(2,a?n.length-7:void 0),o=e[Qe]||null,o=o==null?null:o[n],typeof o==`function`&&e.removeEventListener(t,o,a),typeof r==`function`)){typeof o!=`function`&&o!==null&&(n in e?e[n]=null:e.hasAttribute(n)&&e.removeAttribute(n)),e.addEventListener(t,r,a);break a}n in e?e[n]=r:!0===r?e.setAttribute(n,``):yt(e,n,r)}}}function Pd(e,t,n){switch(t){case`div`:case`span`:case`svg`:case`path`:case`a`:case`g`:case`p`:case`li`:break;case`img`:vd(`error`,e),vd(`load`,e);var r=!1,a=!1,o;for(o in n)if(n.hasOwnProperty(o)){var s=n[o];if(s!=null)switch(o){case`src`:r=!0;break;case`srcSet`:a=!0;break;case`children`:case`dangerouslySetInnerHTML`:throw Error(i(137,t));default:Md(e,t,o,s,n,null)}}a&&Md(e,t,`srcSet`,n.srcSet,n,null),r&&Md(e,t,`src`,n.src,n,null);return;case`input`:vd(`invalid`,e);var c=o=s=a=null,l=null,u=null;for(r in n)if(n.hasOwnProperty(r)){var d=n[r];if(d!=null)switch(r){case`name`:a=d;break;case`type`:s=d;break;case`checked`:l=d;break;case`defaultChecked`:u=d;break;case`value`:o=d;break;case`defaultValue`:c=d;break;case`children`:case`dangerouslySetInnerHTML`:if(d!=null)throw Error(i(137,t));break;default:Md(e,t,r,d,n,null)}}jt(e,o,c,l,u,s,a,!1);return;case`select`:for(a in vd(`invalid`,e),r=s=o=null,n)if(n.hasOwnProperty(a)&&(c=n[a],c!=null))switch(a){case`value`:o=c;break;case`defaultValue`:s=c;break;case`multiple`:r=c;default:Md(e,t,a,c,n,null)}t=o,n=s,e.multiple=!!r,t==null?n!=null&&Nt(e,!!r,n,!0):Nt(e,!!r,t,!1);return;case`textarea`:for(s in vd(`invalid`,e),o=a=r=null,n)if(n.hasOwnProperty(s)&&(c=n[s],c!=null))switch(s){case`value`:r=c;break;case`defaultValue`:a=c;break;case`children`:o=c;break;case`dangerouslySetInnerHTML`:if(c!=null)throw Error(i(91));break;default:Md(e,t,s,c,n,null)}Ft(e,r,a,o);return;case`option`:for(l in n)if(n.hasOwnProperty(l)&&(r=n[l],r!=null))switch(l){case`selected`:e.selected=r&&typeof r!=`function`&&typeof r!=`symbol`;break;default:Md(e,t,l,r,n,null)}return;case`dialog`:vd(`beforetoggle`,e),vd(`toggle`,e),vd(`cancel`,e),vd(`close`,e);break;case`iframe`:case`object`:vd(`load`,e);break;case`video`:case`audio`:for(r=0;r<hd.length;r++)vd(hd[r],e);break;case`image`:vd(`error`,e),vd(`load`,e);break;case`details`:vd(`toggle`,e);break;case`embed`:case`source`:case`link`:vd(`error`,e),vd(`load`,e);case`area`:case`base`:case`br`:case`col`:case`hr`:case`keygen`:case`meta`:case`param`:case`track`:case`wbr`:case`menuitem`:for(u in n)if(n.hasOwnProperty(u)&&(r=n[u],r!=null))switch(u){case`children`:case`dangerouslySetInnerHTML`:throw Error(i(137,t));default:Md(e,t,u,r,n,null)}return;default:if(Bt(t)){for(d in n)n.hasOwnProperty(d)&&(r=n[d],r!==void 0&&Nd(e,t,d,r,n,void 0));return}}for(c in n)n.hasOwnProperty(c)&&(r=n[c],r!=null&&Md(e,t,c,r,n,null))}function Fd(e,t,n,r){switch(t){case`div`:case`span`:case`svg`:case`path`:case`a`:case`g`:case`p`:case`li`:break;case`input`:var a=null,o=null,s=null,c=null,l=null,u=null,d=null;for(m in n){var f=n[m];if(n.hasOwnProperty(m)&&f!=null)switch(m){case`checked`:break;case`value`:break;case`defaultValue`:l=f;default:r.hasOwnProperty(m)||Md(e,t,m,null,r,f)}}for(var p in r){var m=r[p];if(f=n[p],r.hasOwnProperty(p)&&(m!=null||f!=null))switch(p){case`type`:o=m;break;case`name`:a=m;break;case`checked`:u=m;break;case`defaultChecked`:d=m;break;case`value`:s=m;break;case`defaultValue`:c=m;break;case`children`:case`dangerouslySetInnerHTML`:if(m!=null)throw Error(i(137,t));break;default:m!==f&&Md(e,t,p,m,r,f)}}At(e,s,c,l,u,d,o,a);return;case`select`:for(o in m=s=c=p=null,n)if(l=n[o],n.hasOwnProperty(o)&&l!=null)switch(o){case`value`:break;case`multiple`:m=l;default:r.hasOwnProperty(o)||Md(e,t,o,null,r,l)}for(a in r)if(o=r[a],l=n[a],r.hasOwnProperty(a)&&(o!=null||l!=null))switch(a){case`value`:p=o;break;case`defaultValue`:c=o;break;case`multiple`:s=o;default:o!==l&&Md(e,t,a,o,r,l)}t=c,n=s,r=m,p==null?!!r!=!!n&&(t==null?Nt(e,!!n,n?[]:``,!1):Nt(e,!!n,t,!0)):Nt(e,!!n,p,!1);return;case`textarea`:for(c in m=p=null,n)if(a=n[c],n.hasOwnProperty(c)&&a!=null&&!r.hasOwnProperty(c))switch(c){case`value`:break;case`children`:break;default:Md(e,t,c,null,r,a)}for(s in r)if(a=r[s],o=n[s],r.hasOwnProperty(s)&&(a!=null||o!=null))switch(s){case`value`:p=a;break;case`defaultValue`:m=a;break;case`children`:break;case`dangerouslySetInnerHTML`:if(a!=null)throw Error(i(91));break;default:a!==o&&Md(e,t,s,a,r,o)}Pt(e,p,m);return;case`option`:for(var h in n)if(p=n[h],n.hasOwnProperty(h)&&p!=null&&!r.hasOwnProperty(h))switch(h){case`selected`:e.selected=!1;break;default:Md(e,t,h,null,r,p)}for(l in r)if(p=r[l],m=n[l],r.hasOwnProperty(l)&&p!==m&&(p!=null||m!=null))switch(l){case`selected`:e.selected=p&&typeof p!=`function`&&typeof p!=`symbol`;break;default:Md(e,t,l,p,r,m)}return;case`img`:case`link`:case`area`:case`base`:case`br`:case`col`:case`embed`:case`hr`:case`keygen`:case`meta`:case`param`:case`source`:case`track`:case`wbr`:case`menuitem`:for(var g in n)p=n[g],n.hasOwnProperty(g)&&p!=null&&!r.hasOwnProperty(g)&&Md(e,t,g,null,r,p);for(u in r)if(p=r[u],m=n[u],r.hasOwnProperty(u)&&p!==m&&(p!=null||m!=null))switch(u){case`children`:case`dangerouslySetInnerHTML`:if(p!=null)throw Error(i(137,t));break;default:Md(e,t,u,p,r,m)}return;default:if(Bt(t)){for(var _ in n)p=n[_],n.hasOwnProperty(_)&&p!==void 0&&!r.hasOwnProperty(_)&&Nd(e,t,_,void 0,r,p);for(d in r)p=r[d],m=n[d],!r.hasOwnProperty(d)||p===m||p===void 0&&m===void 0||Nd(e,t,d,p,r,m);return}}for(var v in n)p=n[v],n.hasOwnProperty(v)&&p!=null&&!r.hasOwnProperty(v)&&Md(e,t,v,null,r,p);for(f in r)p=r[f],m=n[f],!r.hasOwnProperty(f)||p===m||p==null&&m==null||Md(e,t,f,p,r,m)}function Id(e){switch(e){case`css`:case`script`:case`font`:case`img`:case`image`:case`input`:case`link`:return!0;default:return!1}}function Ld(){if(typeof performance.getEntriesByType==`function`){for(var e=0,t=0,n=performance.getEntriesByType(`resource`),r=0;r<n.length;r++){var i=n[r],a=i.transferSize,o=i.initiatorType,s=i.duration;if(a&&s&&Id(o)){for(o=0,s=i.responseEnd,r+=1;r<n.length;r++){var c=n[r],l=c.startTime;if(l>s)break;var u=c.transferSize,d=c.initiatorType;u&&Id(d)&&(c=c.responseEnd,o+=u*(c<s?1:(s-l)/(c-l)))}if(--r,t+=8*(a+o)/(i.duration/1e3),e++,10<e)break}}if(0<e)return t/e/1e6}return navigator.connection&&(e=navigator.connection.downlink,typeof e==`number`)?e:5}var Rd=null,zd=null;function Bd(e){return e.nodeType===9?e:e.ownerDocument}function Vd(e){switch(e){case`http://www.w3.org/2000/svg`:return 1;case`http://www.w3.org/1998/Math/MathML`:return 2;default:return 0}}function Hd(e,t){if(e===0)switch(t){case`svg`:return 1;case`math`:return 2;default:return 0}return e===1&&t===`foreignObject`?0:e}function Ud(e,t){return e===`textarea`||e===`noscript`||typeof t.children==`string`||typeof t.children==`number`||typeof t.children==`bigint`||typeof t.dangerouslySetInnerHTML==`object`&&t.dangerouslySetInnerHTML!==null&&t.dangerouslySetInnerHTML.__html!=null}var Wd=null;function Gd(){var e=window.event;return e&&e.type===`popstate`?e!==Wd&&(Wd=e,!0):(Wd=null,!1)}var Kd=typeof setTimeout==`function`?setTimeout:void 0,qd=typeof clearTimeout==`function`?clearTimeout:void 0,Jd=typeof Promise==`function`?Promise:void 0,Yd=typeof queueMicrotask==`function`?queueMicrotask:Jd===void 0?Kd:function(e){return Jd.resolve(null).then(e).catch(Xd)};function Xd(e){setTimeout(function(){throw e})}function Zd(e){return e===`head`}function Qd(e,t){var n=t,r=0;do{var i=n.nextSibling;if(e.removeChild(n),i&&i.nodeType===8){if(n=i.data,n===`/$`||n===`/&`){if(r===0){e.removeChild(i),Np(t);return}r--}else if(n===`$`||n===`$?`||n===`$~`||n===`$!`||n===`&`)r++;else if(n===`html`)pf(e.ownerDocument.documentElement);else if(n===`head`){n=e.ownerDocument.head,pf(n);for(var a=n.firstChild;a;){var o=a.nextSibling,s=a.nodeName;a[it]||s===`SCRIPT`||s===`STYLE`||s===`LINK`&&a.rel.toLowerCase()===`stylesheet`||n.removeChild(a),a=o}}else n===`body`&&pf(e.ownerDocument.body)}n=i}while(n);Np(t)}function $d(e,t){var n=e;e=0;do{var r=n.nextSibling;if(n.nodeType===1?t?(n._stashedDisplay=n.style.display,n.style.display=`none`):(n.style.display=n._stashedDisplay||``,n.getAttribute(`style`)===``&&n.removeAttribute(`style`)):n.nodeType===3&&(t?(n._stashedText=n.nodeValue,n.nodeValue=``):n.nodeValue=n._stashedText||``),r&&r.nodeType===8){if(n=r.data,n===`/$`){if(e===0)break;e--}else n!==`$`&&n!==`$?`&&n!==`$~`&&n!==`$!`||e++}n=r}while(n)}function ef(e){var t=e.firstChild;for(t&&t.nodeType===10&&(t=t.nextSibling);t;){var n=t;switch(t=t.nextSibling,n.nodeName){case`HTML`:case`HEAD`:case`BODY`:ef(n),at(n);continue;case`SCRIPT`:case`STYLE`:continue;case`LINK`:if(n.rel.toLowerCase()===`stylesheet`)continue}e.removeChild(n)}}function tf(e,t,n,r){for(;e.nodeType===1;){var i=n;if(e.nodeName.toLowerCase()!==t.toLowerCase()){if(!r&&(e.nodeName!==`INPUT`||e.type!==`hidden`))break}else if(!r){if(t===`input`&&e.type===`hidden`){var a=i.name==null?null:``+i.name;if(i.type===`hidden`&&e.getAttribute(`name`)===a)return e}else return e}else if(!e[it])switch(t){case`meta`:if(!e.hasAttribute(`itemprop`))break;return e;case`link`:if(a=e.getAttribute(`rel`),a===`stylesheet`&&e.hasAttribute(`data-precedence`)||a!==i.rel||e.getAttribute(`href`)!==(i.href==null||i.href===``?null:i.href)||e.getAttribute(`crossorigin`)!==(i.crossOrigin==null?null:i.crossOrigin)||e.getAttribute(`title`)!==(i.title==null?null:i.title))break;return e;case`style`:if(e.hasAttribute(`data-precedence`))break;return e;case`script`:if(a=e.getAttribute(`src`),(a!==(i.src==null?null:i.src)||e.getAttribute(`type`)!==(i.type==null?null:i.type)||e.getAttribute(`crossorigin`)!==(i.crossOrigin==null?null:i.crossOrigin))&&a&&e.hasAttribute(`async`)&&!e.hasAttribute(`itemprop`))break;return e;default:return e}if(e=cf(e.nextSibling),e===null)break}return null}function nf(e,t,n){if(t===``)return null;for(;e.nodeType!==3;)if((e.nodeType!==1||e.nodeName!==`INPUT`||e.type!==`hidden`)&&!n||(e=cf(e.nextSibling),e===null))return null;return e}function rf(e,t){for(;e.nodeType!==8;)if((e.nodeType!==1||e.nodeName!==`INPUT`||e.type!==`hidden`)&&!t||(e=cf(e.nextSibling),e===null))return null;return e}function af(e){return e.data===`$?`||e.data===`$~`}function of(e){return e.data===`$!`||e.data===`$?`&&e.ownerDocument.readyState!==`loading`}function sf(e,t){var n=e.ownerDocument;if(e.data===`$~`)e._reactRetry=t;else if(e.data!==`$?`||n.readyState!==`loading`)t();else{var r=function(){t(),n.removeEventListener(`DOMContentLoaded`,r)};n.addEventListener(`DOMContentLoaded`,r),e._reactRetry=r}}function cf(e){for(;e!=null;e=e.nextSibling){var t=e.nodeType;if(t===1||t===3)break;if(t===8){if(t=e.data,t===`$`||t===`$!`||t===`$?`||t===`$~`||t===`&`||t===`F!`||t===`F`)break;if(t===`/$`||t===`/&`)return null}}return e}var lf=null;function uf(e){e=e.nextSibling;for(var t=0;e;){if(e.nodeType===8){var n=e.data;if(n===`/$`||n===`/&`){if(t===0)return cf(e.nextSibling);t--}else n!==`$`&&n!==`$!`&&n!==`$?`&&n!==`$~`&&n!==`&`||t++}e=e.nextSibling}return null}function df(e){e=e.previousSibling;for(var t=0;e;){if(e.nodeType===8){var n=e.data;if(n===`$`||n===`$!`||n===`$?`||n===`$~`||n===`&`){if(t===0)return e;t--}else n!==`/$`&&n!==`/&`||t++}e=e.previousSibling}return null}function ff(e,t,n){switch(t=Bd(n),e){case`html`:if(e=t.documentElement,!e)throw Error(i(452));return e;case`head`:if(e=t.head,!e)throw Error(i(453));return e;case`body`:if(e=t.body,!e)throw Error(i(454));return e;default:throw Error(i(451))}}function pf(e){for(var t=e.attributes;t.length;)e.removeAttributeNode(t[0]);at(e)}var mf=new Map,hf=new Set;function gf(e){return typeof e.getRootNode==`function`?e.getRootNode():e.nodeType===9?e:e.ownerDocument}var _f=L.d;L.d={f:vf,r:yf,D:Sf,C:Cf,L:wf,m:Tf,X:Df,S:Ef,M:Of};function vf(){var e=_f.f(),t=_u();return e||t}function yf(e){var t=st(e);t!==null&&t.tag===5&&t.type===`form`?gs(t):_f.r(e)}var bf=typeof document>`u`?null:document;function xf(e,t,n){var r=bf;if(r&&typeof t==`string`&&t){var i=kt(t);i=`link[rel="`+e+`"][href="`+i+`"]`,typeof n==`string`&&(i+=`[crossorigin="`+n+`"]`),hf.has(i)||(hf.add(i),e={rel:e,crossOrigin:n,href:t},r.querySelector(i)===null&&(t=r.createElement(`link`),Pd(t,`link`,e),ut(t),r.head.appendChild(t)))}}function Sf(e){_f.D(e),xf(`dns-prefetch`,e,null)}function Cf(e,t){_f.C(e,t),xf(`preconnect`,e,t)}function wf(e,t,n){_f.L(e,t,n);var r=bf;if(r&&e&&t){var i=`link[rel="preload"][as="`+kt(t)+`"]`;t===`image`&&n&&n.imageSrcSet?(i+=`[imagesrcset="`+kt(n.imageSrcSet)+`"]`,typeof n.imageSizes==`string`&&(i+=`[imagesizes="`+kt(n.imageSizes)+`"]`)):i+=`[href="`+kt(e)+`"]`;var a=i;switch(t){case`style`:a=Af(e);break;case`script`:a=Pf(e)}mf.has(a)||(e=h({rel:`preload`,href:t===`image`&&n&&n.imageSrcSet?void 0:e,as:t},n),mf.set(a,e),r.querySelector(i)!==null||t===`style`&&r.querySelector(jf(a))||t===`script`&&r.querySelector(Ff(a))||(t=r.createElement(`link`),Pd(t,`link`,e),ut(t),r.head.appendChild(t)))}}function Tf(e,t){_f.m(e,t);var n=bf;if(n&&e){var r=t&&typeof t.as==`string`?t.as:`script`,i=`link[rel="modulepreload"][as="`+kt(r)+`"][href="`+kt(e)+`"]`,a=i;switch(r){case`audioworklet`:case`paintworklet`:case`serviceworker`:case`sharedworker`:case`worker`:case`script`:a=Pf(e)}if(!mf.has(a)&&(e=h({rel:`modulepreload`,href:e},t),mf.set(a,e),n.querySelector(i)===null)){switch(r){case`audioworklet`:case`paintworklet`:case`serviceworker`:case`sharedworker`:case`worker`:case`script`:if(n.querySelector(Ff(a)))return}r=n.createElement(`link`),Pd(r,`link`,e),ut(r),n.head.appendChild(r)}}}function Ef(e,t,n){_f.S(e,t,n);var r=bf;if(r&&e){var i=lt(r).hoistableStyles,a=Af(e);t||=`default`;var o=i.get(a);if(!o){var s={loading:0,preload:null};if(o=r.querySelector(jf(a)))s.loading=5;else{e=h({rel:`stylesheet`,href:e,"data-precedence":t},n),(n=mf.get(a))&&Rf(e,n);var c=o=r.createElement(`link`);ut(c),Pd(c,`link`,e),c._p=new Promise(function(e,t){c.onload=e,c.onerror=t}),c.addEventListener(`load`,function(){s.loading|=1}),c.addEventListener(`error`,function(){s.loading|=2}),s.loading|=4,Lf(o,t,r)}o={type:`stylesheet`,instance:o,count:1,state:s},i.set(a,o)}}}function Df(e,t){_f.X(e,t);var n=bf;if(n&&e){var r=lt(n).hoistableScripts,i=Pf(e),a=r.get(i);a||(a=n.querySelector(Ff(i)),a||(e=h({src:e,async:!0},t),(t=mf.get(i))&&zf(e,t),a=n.createElement(`script`),ut(a),Pd(a,`link`,e),n.head.appendChild(a)),a={type:`script`,instance:a,count:1,state:null},r.set(i,a))}}function Of(e,t){_f.M(e,t);var n=bf;if(n&&e){var r=lt(n).hoistableScripts,i=Pf(e),a=r.get(i);a||(a=n.querySelector(Ff(i)),a||(e=h({src:e,async:!0,type:`module`},t),(t=mf.get(i))&&zf(e,t),a=n.createElement(`script`),ut(a),Pd(a,`link`,e),n.head.appendChild(a)),a={type:`script`,instance:a,count:1,state:null},r.set(i,a))}}function kf(e,t,n,r){var a=(a=te.current)?gf(a):null;if(!a)throw Error(i(446));switch(e){case`meta`:case`title`:return null;case`style`:return typeof n.precedence==`string`&&typeof n.href==`string`?(t=Af(n.href),n=lt(a).hoistableStyles,r=n.get(t),r||(r={type:`style`,instance:null,count:0,state:null},n.set(t,r)),r):{type:`void`,instance:null,count:0,state:null};case`link`:if(n.rel===`stylesheet`&&typeof n.href==`string`&&typeof n.precedence==`string`){e=Af(n.href);var o=lt(a).hoistableStyles,s=o.get(e);if(s||(a=a.ownerDocument||a,s={type:`stylesheet`,instance:null,count:0,state:{loading:0,preload:null}},o.set(e,s),(o=a.querySelector(jf(e)))&&!o._p&&(s.instance=o,s.state.loading=5),mf.has(e)||(n={rel:`preload`,as:`style`,href:n.href,crossOrigin:n.crossOrigin,integrity:n.integrity,media:n.media,hrefLang:n.hrefLang,referrerPolicy:n.referrerPolicy},mf.set(e,n),o||Nf(a,e,n,s.state))),t&&r===null)throw Error(i(528,``));return s}if(t&&r!==null)throw Error(i(529,``));return null;case`script`:return t=n.async,n=n.src,typeof n==`string`&&t&&typeof t!=`function`&&typeof t!=`symbol`?(t=Pf(n),n=lt(a).hoistableScripts,r=n.get(t),r||(r={type:`script`,instance:null,count:0,state:null},n.set(t,r)),r):{type:`void`,instance:null,count:0,state:null};default:throw Error(i(444,e))}}function Af(e){return`href="`+kt(e)+`"`}function jf(e){return`link[rel="stylesheet"][`+e+`]`}function Mf(e){return h({},e,{"data-precedence":e.precedence,precedence:null})}function Nf(e,t,n,r){e.querySelector(`link[rel="preload"][as="style"][`+t+`]`)?r.loading=1:(t=e.createElement(`link`),r.preload=t,t.addEventListener(`load`,function(){return r.loading|=1}),t.addEventListener(`error`,function(){return r.loading|=2}),Pd(t,`link`,n),ut(t),e.head.appendChild(t))}function Pf(e){return`[src="`+kt(e)+`"]`}function Ff(e){return`script[async]`+e}function If(e,t,n){if(t.count++,t.instance===null)switch(t.type){case`style`:var r=e.querySelector(`style[data-href~="`+kt(n.href)+`"]`);if(r)return t.instance=r,ut(r),r;var a=h({},n,{"data-href":n.href,"data-precedence":n.precedence,href:null,precedence:null});return r=(e.ownerDocument||e).createElement(`style`),ut(r),Pd(r,`style`,a),Lf(r,n.precedence,e),t.instance=r;case`stylesheet`:a=Af(n.href);var o=e.querySelector(jf(a));if(o)return t.state.loading|=4,t.instance=o,ut(o),o;r=Mf(n),(a=mf.get(a))&&Rf(r,a),o=(e.ownerDocument||e).createElement(`link`),ut(o);var s=o;return s._p=new Promise(function(e,t){s.onload=e,s.onerror=t}),Pd(o,`link`,r),t.state.loading|=4,Lf(o,n.precedence,e),t.instance=o;case`script`:return o=Pf(n.src),(a=e.querySelector(Ff(o)))?(t.instance=a,ut(a),a):(r=n,(a=mf.get(o))&&(r=h({},n),zf(r,a)),e=e.ownerDocument||e,a=e.createElement(`script`),ut(a),Pd(a,`link`,r),e.head.appendChild(a),t.instance=a);case`void`:return null;default:throw Error(i(443,t.type))}else t.type===`stylesheet`&&!(t.state.loading&4)&&(r=t.instance,t.state.loading|=4,Lf(r,n.precedence,e));return t.instance}function Lf(e,t,n){for(var r=n.querySelectorAll(`link[rel="stylesheet"][data-precedence],style[data-precedence]`),i=r.length?r[r.length-1]:null,a=i,o=0;o<r.length;o++){var s=r[o];if(s.dataset.precedence===t)a=s;else if(a!==i)break}a?a.parentNode.insertBefore(e,a.nextSibling):(t=n.nodeType===9?n.head:n,t.insertBefore(e,t.firstChild))}function Rf(e,t){e.crossOrigin??=t.crossOrigin,e.referrerPolicy??=t.referrerPolicy,e.title??=t.title}function zf(e,t){e.crossOrigin??=t.crossOrigin,e.referrerPolicy??=t.referrerPolicy,e.integrity??=t.integrity}var Bf=null;function Vf(e,t,n){if(Bf===null){var r=new Map,i=Bf=new Map;i.set(n,r)}else i=Bf,r=i.get(n),r||(r=new Map,i.set(n,r));if(r.has(e))return r;for(r.set(e,null),n=n.getElementsByTagName(e),i=0;i<n.length;i++){var a=n[i];if(!(a[it]||a[Ze]||e===`link`&&a.getAttribute(`rel`)===`stylesheet`)&&a.namespaceURI!==`http://www.w3.org/2000/svg`){var o=a.getAttribute(t)||``;o=e+o;var s=r.get(o);s?s.push(a):r.set(o,[a])}}return r}function Hf(e,t,n){e=e.ownerDocument||e,e.head.insertBefore(n,t===`title`?e.querySelector(`head > title`):null)}function Uf(e,t,n){if(n===1||t.itemProp!=null)return!1;switch(e){case`meta`:case`title`:return!0;case`style`:if(typeof t.precedence!=`string`||typeof t.href!=`string`||t.href===``)break;return!0;case`link`:if(typeof t.rel!=`string`||typeof t.href!=`string`||t.href===``||t.onLoad||t.onError)break;switch(t.rel){case`stylesheet`:return e=t.disabled,typeof t.precedence==`string`&&e==null;default:return!0}case`script`:if(t.async&&typeof t.async!=`function`&&typeof t.async!=`symbol`&&!t.onLoad&&!t.onError&&t.src&&typeof t.src==`string`)return!0}return!1}function Wf(e){return!(e.type===`stylesheet`&&!(e.state.loading&3))}function Gf(e,t,n,r){if(n.type===`stylesheet`&&(typeof r.media!=`string`||!1!==matchMedia(r.media).matches)&&!(n.state.loading&4)){if(n.instance===null){var i=Af(r.href),a=t.querySelector(jf(i));if(a){t=a._p,typeof t==`object`&&t&&typeof t.then==`function`&&(e.count++,e=Jf.bind(e),t.then(e,e)),n.state.loading|=4,n.instance=a,ut(a);return}a=t.ownerDocument||t,r=Mf(r),(i=mf.get(i))&&Rf(r,i),a=a.createElement(`link`),ut(a);var o=a;o._p=new Promise(function(e,t){o.onload=e,o.onerror=t}),Pd(a,`link`,r),n.instance=a}e.stylesheets===null&&(e.stylesheets=new Map),e.stylesheets.set(n,t),(t=n.state.preload)&&!(n.state.loading&3)&&(e.count++,n=Jf.bind(e),t.addEventListener(`load`,n),t.addEventListener(`error`,n))}}var Kf=0;function qf(e,t){return e.stylesheets&&e.count===0&&Xf(e,e.stylesheets),0<e.count||0<e.imgCount?function(n){var r=setTimeout(function(){if(e.stylesheets&&Xf(e,e.stylesheets),e.unsuspend){var t=e.unsuspend;e.unsuspend=null,t()}},6e4+t);0<e.imgBytes&&Kf===0&&(Kf=62500*Ld());var i=setTimeout(function(){if(e.waitingForImages=!1,e.count===0&&(e.stylesheets&&Xf(e,e.stylesheets),e.unsuspend)){var t=e.unsuspend;e.unsuspend=null,t()}},(e.imgBytes>Kf?50:800)+t);return e.unsuspend=n,function(){e.unsuspend=null,clearTimeout(r),clearTimeout(i)}}:null}function Jf(){if(this.count--,this.count===0&&(this.imgCount===0||!this.waitingForImages)){if(this.stylesheets)Xf(this,this.stylesheets);else if(this.unsuspend){var e=this.unsuspend;this.unsuspend=null,e()}}}var Yf=null;function Xf(e,t){e.stylesheets=null,e.unsuspend!==null&&(e.count++,Yf=new Map,t.forEach(Zf,e),Yf=null,Jf.call(e))}function Zf(e,t){if(!(t.state.loading&4)){var n=Yf.get(e);if(n)var r=n.get(null);else{n=new Map,Yf.set(e,n);for(var i=e.querySelectorAll(`link[data-precedence],style[data-precedence]`),a=0;a<i.length;a++){var o=i[a];(o.nodeName===`LINK`||o.getAttribute(`media`)!==`not all`)&&(n.set(o.dataset.precedence,o),r=o)}r&&n.set(null,r)}i=t.instance,o=i.getAttribute(`data-precedence`),a=n.get(o)||r,a===r&&n.set(null,i),n.set(o,i),this.count++,r=Jf.bind(this),i.addEventListener(`load`,r),i.addEventListener(`error`,r),a?a.parentNode.insertBefore(i,a.nextSibling):(e=e.nodeType===9?e.head:e,e.insertBefore(i,e.firstChild)),t.state.loading|=4}}var Qf={$$typeof:C,Provider:null,Consumer:null,_currentValue:R,_currentValue2:R,_threadCount:0};function $f(e,t,n,r,i,a,o,s,c){this.tag=1,this.containerInfo=e,this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.next=this.pendingContext=this.context=this.cancelPendingCommit=null,this.callbackPriority=0,this.expirationTimes=Be(-1),this.entangledLanes=this.shellSuspendCounter=this.errorRecoveryDisabledLanes=this.expiredLanes=this.warmLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=Be(0),this.hiddenUpdates=Be(null),this.identifierPrefix=r,this.onUncaughtError=i,this.onCaughtError=a,this.onRecoverableError=o,this.pooledCache=null,this.pooledCacheLanes=0,this.formState=c,this.incompleteTransitions=new Map}function ep(e,t,n,r,i,a,o,s,c,l,u,d){return e=new $f(e,t,n,o,c,l,u,d,s),t=1,!0===a&&(t|=24),a=Yr(3,null,null,t),e.current=a,a.stateNode=e,t=Yi(),t.refCount++,e.pooledCache=t,t.refCount++,a.memoizedState={element:r,isDehydrated:n,cache:t},Oa(a),e}function tp(e){return e?(e=qr,e):qr}function np(e,t,n,r,i,a){i=tp(i),r.context===null?r.context=i:r.pendingContext=i,r=Aa(t),r.payload={element:n},a=a===void 0?null:a,a!==null&&(r.callback=a),n=ja(e,r,t),n!==null&&(fu(n,e,t),Ma(n,e,t))}function rp(e,t){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var n=e.retryLane;e.retryLane=n!==0&&n<t?n:t}}function ip(e,t){rp(e,t),(e=e.alternate)&&rp(e,t)}function ap(e){if(e.tag===13||e.tag===31){var t=Wr(e,67108864);t!==null&&fu(t,e,67108864),ip(e,67108864)}}function op(e){if(e.tag===13||e.tag===31){var t=uu();t=Ke(t);var n=Wr(e,t);n!==null&&fu(n,e,t),ip(e,t)}}var sp=!0;function cp(e,t,n,r){var i=I.T;I.T=null;var a=L.p;try{L.p=2,up(e,t,n,r)}finally{L.p=a,I.T=i}}function lp(e,t,n,r){var i=I.T;I.T=null;var a=L.p;try{L.p=8,up(e,t,n,r)}finally{L.p=a,I.T=i}}function up(e,t,n,r){if(sp){var i=dp(r);if(i===null)Cd(e,t,r,fp,n),Cp(e,r);else if(Tp(i,e,t,n,r))r.stopPropagation();else if(Cp(e,r),t&4&&-1<Sp.indexOf(e)){for(;i!==null;){var a=st(i);if(a!==null)switch(a.tag){case 3:if(a=a.stateNode,a.current.memoizedState.isDehydrated){var o=Fe(a.pendingLanes);if(o!==0){var s=a;for(s.pendingLanes|=2,s.entangledLanes|=2;o;){var c=1<<31-Oe(o);s.entanglements[1]|=c,o&=~c}td(a),!(jl&6)&&(Ql=ve()+500,nd(0,!1))}}break;case 31:case 13:s=Wr(a,2),s!==null&&fu(s,a,2),_u(),ip(a,2)}if(a=dp(r),a===null&&Cd(e,t,r,fp,n),a===i)break;i=a}i!==null&&r.stopPropagation()}else Cd(e,t,r,null,n)}}function dp(e){return e=Kt(e),pp(e)}var fp=null;function pp(e){if(fp=null,e=ot(e),e!==null){var t=o(e);if(t===null)e=null;else{var n=t.tag;if(n===13){if(e=s(t),e!==null)return e;e=null}else if(n===31){if(e=c(t),e!==null)return e;e=null}else if(n===3){if(t.stateNode.current.memoizedState.isDehydrated)return t.tag===3?t.stateNode.containerInfo:null;e=null}else t!==e&&(e=null)}}return fp=e,null}function mp(e){switch(e){case`beforetoggle`:case`cancel`:case`click`:case`close`:case`contextmenu`:case`copy`:case`cut`:case`auxclick`:case`dblclick`:case`dragend`:case`dragstart`:case`drop`:case`focusin`:case`focusout`:case`input`:case`invalid`:case`keydown`:case`keypress`:case`keyup`:case`mousedown`:case`mouseup`:case`paste`:case`pause`:case`play`:case`pointercancel`:case`pointerdown`:case`pointerup`:case`ratechange`:case`reset`:case`resize`:case`seeked`:case`submit`:case`toggle`:case`touchcancel`:case`touchend`:case`touchstart`:case`volumechange`:case`change`:case`selectionchange`:case`textInput`:case`compositionstart`:case`compositionend`:case`compositionupdate`:case`beforeblur`:case`afterblur`:case`beforeinput`:case`blur`:case`fullscreenchange`:case`focus`:case`hashchange`:case`popstate`:case`select`:case`selectstart`:return 2;case`drag`:case`dragenter`:case`dragexit`:case`dragleave`:case`dragover`:case`mousemove`:case`mouseout`:case`mouseover`:case`pointermove`:case`pointerout`:case`pointerover`:case`scroll`:case`touchmove`:case`wheel`:case`mouseenter`:case`mouseleave`:case`pointerenter`:case`pointerleave`:return 8;case`message`:switch(ye()){case K:return 2;case be:return 8;case xe:case q:return 32;case Se:return 268435456;default:return 32}default:return 32}}var hp=!1,gp=null,_p=null,vp=null,yp=new Map,bp=new Map,xp=[],Sp=`mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset`.split(` `);function Cp(e,t){switch(e){case`focusin`:case`focusout`:gp=null;break;case`dragenter`:case`dragleave`:_p=null;break;case`mouseover`:case`mouseout`:vp=null;break;case`pointerover`:case`pointerout`:yp.delete(t.pointerId);break;case`gotpointercapture`:case`lostpointercapture`:bp.delete(t.pointerId)}}function wp(e,t,n,r,i,a){return e===null||e.nativeEvent!==a?(e={blockedOn:t,domEventName:n,eventSystemFlags:r,nativeEvent:a,targetContainers:[i]},t!==null&&(t=st(t),t!==null&&ap(t)),e):(e.eventSystemFlags|=r,t=e.targetContainers,i!==null&&t.indexOf(i)===-1&&t.push(i),e)}function Tp(e,t,n,r,i){switch(t){case`focusin`:return gp=wp(gp,e,t,n,r,i),!0;case`dragenter`:return _p=wp(_p,e,t,n,r,i),!0;case`mouseover`:return vp=wp(vp,e,t,n,r,i),!0;case`pointerover`:var a=i.pointerId;return yp.set(a,wp(yp.get(a)||null,e,t,n,r,i)),!0;case`gotpointercapture`:return a=i.pointerId,bp.set(a,wp(bp.get(a)||null,e,t,n,r,i)),!0}return!1}function Ep(e){var t=ot(e.target);if(t!==null){var n=o(t);if(n!==null){if(t=n.tag,t===13){if(t=s(n),t!==null){e.blockedOn=t,Ye(e.priority,function(){op(n)});return}}else if(t===31){if(t=c(n),t!==null){e.blockedOn=t,Ye(e.priority,function(){op(n)});return}}else if(t===3&&n.stateNode.current.memoizedState.isDehydrated){e.blockedOn=n.tag===3?n.stateNode.containerInfo:null;return}}}e.blockedOn=null}function Dp(e){if(e.blockedOn!==null)return!1;for(var t=e.targetContainers;0<t.length;){var n=dp(e.nativeEvent);if(n===null){n=e.nativeEvent;var r=new n.constructor(n.type,n);Gt=r,n.target.dispatchEvent(r),Gt=null}else return t=st(n),t!==null&&ap(t),e.blockedOn=n,!1;t.shift()}return!0}function Op(e,t,n){Dp(e)&&n.delete(t)}function kp(){hp=!1,gp!==null&&Dp(gp)&&(gp=null),_p!==null&&Dp(_p)&&(_p=null),vp!==null&&Dp(vp)&&(vp=null),yp.forEach(Op),bp.forEach(Op)}function Ap(e,n){e.blockedOn===n&&(e.blockedOn=null,hp||(hp=!0,t.unstable_scheduleCallback(t.unstable_NormalPriority,kp)))}var jp=null;function Mp(e){jp!==e&&(jp=e,t.unstable_scheduleCallback(t.unstable_NormalPriority,function(){jp===e&&(jp=null);for(var t=0;t<e.length;t+=3){var n=e[t],r=e[t+1],i=e[t+2];if(typeof r!=`function`){if(pp(r||n)===null)continue;break}var a=st(n);a!==null&&(e.splice(t,3),t-=3,ms(a,{pending:!0,data:i,method:n.method,action:r},r,i))}}))}function Np(e){function t(t){return Ap(t,e)}gp!==null&&Ap(gp,e),_p!==null&&Ap(_p,e),vp!==null&&Ap(vp,e),yp.forEach(t),bp.forEach(t);for(var n=0;n<xp.length;n++){var r=xp[n];r.blockedOn===e&&(r.blockedOn=null)}for(;0<xp.length&&(n=xp[0],n.blockedOn===null);)Ep(n),n.blockedOn===null&&xp.shift();if(n=(e.ownerDocument||e).$$reactFormReplay,n!=null)for(r=0;r<n.length;r+=3){var i=n[r],a=n[r+1],o=i[Qe]||null;if(typeof a==`function`)o||Mp(n);else if(o){var s=null;if(a&&a.hasAttribute(`formAction`)){if(i=a,o=a[Qe]||null)s=o.formAction;else if(pp(i)!==null)continue}else s=o.action;typeof s==`function`?n[r+1]=s:(n.splice(r,3),r-=3),Mp(n)}}}function Pp(){function e(e){e.canIntercept&&e.info===`react-transition`&&e.intercept({handler:function(){return new Promise(function(e){return i=e})},focusReset:`manual`,scroll:`manual`})}function t(){i!==null&&(i(),i=null),r||setTimeout(n,20)}function n(){if(!r&&!navigation.transition){var e=navigation.currentEntry;e&&e.url!=null&&navigation.navigate(e.url,{state:e.getState(),info:`react-transition`,history:`replace`})}}if(typeof navigation==`object`){var r=!1,i=null;return navigation.addEventListener(`navigate`,e),navigation.addEventListener(`navigatesuccess`,t),navigation.addEventListener(`navigateerror`,t),setTimeout(n,100),function(){r=!0,navigation.removeEventListener(`navigate`,e),navigation.removeEventListener(`navigatesuccess`,t),navigation.removeEventListener(`navigateerror`,t),i!==null&&(i(),i=null)}}}function Fp(e){this._internalRoot=e}Ip.prototype.render=Fp.prototype.render=function(e){var t=this._internalRoot;if(t===null)throw Error(i(409));var n=t.current;np(n,uu(),e,t,null,null)},Ip.prototype.unmount=Fp.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var t=e.containerInfo;np(e.current,2,null,e,null,null),_u(),t[$e]=null}};function Ip(e){this._internalRoot=e}Ip.prototype.unstable_scheduleHydration=function(e){if(e){var t=Je();e={blockedOn:null,target:e,priority:t};for(var n=0;n<xp.length&&t!==0&&t<xp[n].priority;n++);xp.splice(n,0,e),n===0&&Ep(e)}};var Lp=n.version;if(Lp!==`19.2.8`)throw Error(i(527,Lp,`19.2.8`));L.findDOMNode=function(e){var t=e._reactInternals;if(t===void 0)throw typeof e.render==`function`?Error(i(188)):(e=Object.keys(e).join(`,`),Error(i(268,e)));return e=d(t),e=e===null?null:p(e),e=e===null?null:e.stateNode,e};var Rp={bundleType:0,version:`19.2.8`,rendererPackageName:`react-dom`,currentDispatcherRef:I,reconcilerVersion:`19.2.8`};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<`u`){var zp=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!zp.isDisabled&&zp.supportsFiber)try{Te=zp.inject(Rp),Ee=zp}catch{}}e.createRoot=function(e,t){if(!a(e))throw Error(i(299));var n=!1,r=``,o=Ls,s=Rs,c=zs;return t!=null&&(!0===t.unstable_strictMode&&(n=!0),t.identifierPrefix!==void 0&&(r=t.identifierPrefix),t.onUncaughtError!==void 0&&(o=t.onUncaughtError),t.onCaughtError!==void 0&&(s=t.onCaughtError),t.onRecoverableError!==void 0&&(c=t.onRecoverableError)),t=ep(e,1,!1,null,null,n,r,null,o,s,c,Pp),e[$e]=t.current,xd(e),new Fp(t)}})),g=o(((e,t)=>{function n(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>`u`||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!=`function`))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(n)}catch(e){console.error(e)}}n(),t.exports=h()})),_=c(u(),1),v=new Map([[`bold`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M228,128a100,100,0,0,1-98.66,100H128a99.39,99.39,0,0,1-68.62-27.29,12,12,0,0,1,16.48-17.45,76,76,0,1,0-1.57-109c-.13.13-.25.25-.39.37L54.89,92H72a12,12,0,0,1,0,24H24a12,12,0,0,1-12-12V56a12,12,0,0,1,24,0V76.72L57.48,57.06A100,100,0,0,1,228,128Z`}))],[`duotone`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M216,128a88,88,0,1,1-88-88A88,88,0,0,1,216,128Z`,opacity:`0.2`}),_.createElement(`path`,{d:`M224,128a96,96,0,0,1-94.71,96H128A95.38,95.38,0,0,1,62.1,197.8a8,8,0,0,1,11-11.63A80,80,0,1,0,71.43,71.39a3.07,3.07,0,0,1-.26.25L44.59,96H72a8,8,0,0,1,0,16H24a8,8,0,0,1-8-8V56a8,8,0,0,1,16,0V85.8L60.25,60A96,96,0,0,1,224,128Z`}))],[`fill`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M224,128a96,96,0,0,1-94.71,96H128A95.38,95.38,0,0,1,62.1,197.8a8,8,0,0,1,11-11.63A80,80,0,1,0,71.43,71.39a3.07,3.07,0,0,1-.26.25L60.63,81.29l17,17A8,8,0,0,1,72,112H24a8,8,0,0,1-8-8V56A8,8,0,0,1,29.66,50.3L49.31,70,60.25,60A96,96,0,0,1,224,128Z`}))],[`light`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M222,128a94,94,0,0,1-92.74,94H128a93.43,93.43,0,0,1-64.5-25.65,6,6,0,1,1,8.24-8.72A82,82,0,1,0,70,70l-.19.19L39.44,98H72a6,6,0,0,1,0,12H24a6,6,0,0,1-6-6V56a6,6,0,0,1,12,0V90.34L61.63,61.4A94,94,0,0,1,222,128Z`}))],[`regular`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M224,128a96,96,0,0,1-94.71,96H128A95.38,95.38,0,0,1,62.1,197.8a8,8,0,0,1,11-11.63A80,80,0,1,0,71.43,71.39a3.07,3.07,0,0,1-.26.25L44.59,96H72a8,8,0,0,1,0,16H24a8,8,0,0,1-8-8V56a8,8,0,0,1,16,0V85.8L60.25,60A96,96,0,0,1,224,128Z`}))],[`thin`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M220,128a92,92,0,0,1-90.77,92H128a91.47,91.47,0,0,1-63.13-25.1,4,4,0,1,1,5.5-5.82A84,84,0,1,0,68.6,68.57l-.13.12L34.3,100H72a4,4,0,0,1,0,8H24a4,4,0,0,1-4-4V56a4,4,0,0,1,8,0V94.89l35-32A92,92,0,0,1,220,128Z`}))]]),y=new Map([[`bold`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M216.49,104.49l-80,80a12,12,0,0,1-17,0l-80-80a12,12,0,0,1,17-17L128,159l71.51-71.52a12,12,0,0,1,17,17Z`}))],[`duotone`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M208,96l-80,80L48,96Z`,opacity:`0.2`}),_.createElement(`path`,{d:`M215.39,92.94A8,8,0,0,0,208,88H48a8,8,0,0,0-5.66,13.66l80,80a8,8,0,0,0,11.32,0l80-80A8,8,0,0,0,215.39,92.94ZM128,164.69,67.31,104H188.69Z`}))],[`fill`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M213.66,101.66l-80,80a8,8,0,0,1-11.32,0l-80-80A8,8,0,0,1,48,88H208a8,8,0,0,1,5.66,13.66Z`}))],[`light`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M212.24,100.24l-80,80a6,6,0,0,1-8.48,0l-80-80a6,6,0,0,1,8.48-8.48L128,167.51l75.76-75.75a6,6,0,0,1,8.48,8.48Z`}))],[`regular`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M213.66,101.66l-80,80a8,8,0,0,1-11.32,0l-80-80A8,8,0,0,1,53.66,90.34L128,164.69l74.34-74.35a8,8,0,0,1,11.32,11.32Z`}))],[`thin`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M210.83,98.83l-80,80a4,4,0,0,1-5.66,0l-80-80a4,4,0,0,1,5.66-5.66L128,170.34l77.17-77.17a4,4,0,1,1,5.66,5.66Z`}))]]),b=new Map([[`bold`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M232.49,80.49l-128,128a12,12,0,0,1-17,0l-56-56a12,12,0,1,1,17-17L96,183,215.51,63.51a12,12,0,0,1,17,17Z`}))],[`duotone`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M232,56V200a16,16,0,0,1-16,16H40a16,16,0,0,1-16-16V56A16,16,0,0,1,40,40H216A16,16,0,0,1,232,56Z`,opacity:`0.2`}),_.createElement(`path`,{d:`M205.66,85.66l-96,96a8,8,0,0,1-11.32,0l-40-40a8,8,0,0,1,11.32-11.32L104,164.69l90.34-90.35a8,8,0,0,1,11.32,11.32Z`}))],[`fill`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40ZM205.66,85.66l-96,96a8,8,0,0,1-11.32,0l-40-40a8,8,0,0,1,11.32-11.32L104,164.69l90.34-90.35a8,8,0,0,1,11.32,11.32Z`}))],[`light`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M228.24,76.24l-128,128a6,6,0,0,1-8.48,0l-56-56a6,6,0,0,1,8.48-8.48L96,191.51,219.76,67.76a6,6,0,0,1,8.48,8.48Z`}))],[`regular`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M229.66,77.66l-128,128a8,8,0,0,1-11.32,0l-56-56a8,8,0,0,1,11.32-11.32L96,188.69,218.34,66.34a8,8,0,0,1,11.32,11.32Z`}))],[`thin`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M226.83,74.83l-128,128a4,4,0,0,1-5.66,0l-56-56a4,4,0,0,1,5.66-5.66L96,194.34,221.17,69.17a4,4,0,1,1,5.66,5.66Z`}))]]),x=new Map([[`bold`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M71.68,97.22,34.74,128l36.94,30.78a12,12,0,1,1-15.36,18.44l-48-40a12,12,0,0,1,0-18.44l48-40A12,12,0,0,1,71.68,97.22Zm176,21.56-48-40a12,12,0,1,0-15.36,18.44L221.26,128l-36.94,30.78a12,12,0,1,0,15.36,18.44l48-40a12,12,0,0,0,0-18.44ZM164.1,28.72a12,12,0,0,0-15.38,7.18l-64,176a12,12,0,0,0,7.18,15.37A11.79,11.79,0,0,0,96,228a12,12,0,0,0,11.28-7.9l64-176A12,12,0,0,0,164.1,28.72Z`}))],[`duotone`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M240,128l-48,40H64L16,128,64,88H192Z`,opacity:`0.2`}),_.createElement(`path`,{d:`M69.12,94.15,28.5,128l40.62,33.85a8,8,0,1,1-10.24,12.29l-48-40a8,8,0,0,1,0-12.29l48-40a8,8,0,0,1,10.24,12.3Zm176,27.7-48-40a8,8,0,1,0-10.24,12.3L227.5,128l-40.62,33.85a8,8,0,1,0,10.24,12.29l48-40a8,8,0,0,0,0-12.29ZM162.73,32.48a8,8,0,0,0-10.25,4.79l-64,176a8,8,0,0,0,4.79,10.26A8.14,8.14,0,0,0,96,224a8,8,0,0,0,7.52-5.27l64-176A8,8,0,0,0,162.73,32.48Z`}))],[`fill`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40ZM92.8,145.6a8,8,0,1,1-9.6,12.8l-32-24a8,8,0,0,1,0-12.8l32-24a8,8,0,0,1,9.6,12.8L69.33,128Zm58.89-71.4-32,112a8,8,0,1,1-15.38-4.4l32-112a8,8,0,0,1,15.38,4.4Zm53.11,60.2-32,24a8,8,0,0,1-9.6-12.8L186.67,128,163.2,110.4a8,8,0,1,1,9.6-12.8l32,24a8,8,0,0,1,0,12.8Z`}))],[`light`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M67.84,92.61,25.37,128l42.47,35.39a6,6,0,1,1-7.68,9.22l-48-40a6,6,0,0,1,0-9.22l48-40a6,6,0,0,1,7.68,9.22Zm176,30.78-48-40a6,6,0,1,0-7.68,9.22L230.63,128l-42.47,35.39a6,6,0,1,0,7.68,9.22l48-40a6,6,0,0,0,0-9.22Zm-81.79-89A6,6,0,0,0,154.36,38l-64,176A6,6,0,0,0,94,221.64a6.15,6.15,0,0,0,2,.36,6,6,0,0,0,5.64-3.95l64-176A6,6,0,0,0,162.05,34.36Z`}))],[`regular`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M69.12,94.15,28.5,128l40.62,33.85a8,8,0,1,1-10.24,12.29l-48-40a8,8,0,0,1,0-12.29l48-40a8,8,0,0,1,10.24,12.3Zm176,27.7-48-40a8,8,0,1,0-10.24,12.3L227.5,128l-40.62,33.85a8,8,0,1,0,10.24,12.29l48-40a8,8,0,0,0,0-12.29ZM162.73,32.48a8,8,0,0,0-10.25,4.79l-64,176a8,8,0,0,0,4.79,10.26A8.14,8.14,0,0,0,96,224a8,8,0,0,0,7.52-5.27l64-176A8,8,0,0,0,162.73,32.48Z`}))],[`thin`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M66.56,91.07,22.25,128l44.31,36.93A4,4,0,0,1,64,172a3.94,3.94,0,0,1-2.56-.93l-48-40a4,4,0,0,1,0-6.14l48-40a4,4,0,0,1,5.12,6.14Zm176,33.86-48-40a4,4,0,1,0-5.12,6.14L233.75,128l-44.31,36.93a4,4,0,1,0,5.12,6.14l48-40a4,4,0,0,0,0-6.14ZM161.37,36.24a4,4,0,0,0-5.13,2.39l-64,176a4,4,0,0,0,2.39,5.13A4.12,4.12,0,0,0,96,220a4,4,0,0,0,3.76-2.63l64-176A4,4,0,0,0,161.37,36.24Z`}))]]),S=new Map([[`bold`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M180,64H40A12,12,0,0,0,28,76V216a12,12,0,0,0,12,12H180a12,12,0,0,0,12-12V76A12,12,0,0,0,180,64ZM168,204H52V88H168ZM228,40V180a12,12,0,0,1-24,0V52H76a12,12,0,0,1,0-24H216A12,12,0,0,1,228,40Z`}))],[`duotone`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M184,72V216H40V72Z`,opacity:`0.2`}),_.createElement(`path`,{d:`M184,64H40a8,8,0,0,0-8,8V216a8,8,0,0,0,8,8H184a8,8,0,0,0,8-8V72A8,8,0,0,0,184,64Zm-8,144H48V80H176ZM224,40V184a8,8,0,0,1-16,0V48H72a8,8,0,0,1,0-16H216A8,8,0,0,1,224,40Z`}))],[`fill`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M192,72V216a8,8,0,0,1-8,8H40a8,8,0,0,1-8-8V72a8,8,0,0,1,8-8H184A8,8,0,0,1,192,72Zm24-40H72a8,8,0,0,0,0,16H208V184a8,8,0,0,0,16,0V40A8,8,0,0,0,216,32Z`}))],[`light`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M184,66H40a6,6,0,0,0-6,6V216a6,6,0,0,0,6,6H184a6,6,0,0,0,6-6V72A6,6,0,0,0,184,66Zm-6,144H46V78H178ZM222,40V184a6,6,0,0,1-12,0V46H72a6,6,0,0,1,0-12H216A6,6,0,0,1,222,40Z`}))],[`regular`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M184,64H40a8,8,0,0,0-8,8V216a8,8,0,0,0,8,8H184a8,8,0,0,0,8-8V72A8,8,0,0,0,184,64Zm-8,144H48V80H176ZM224,40V184a8,8,0,0,1-16,0V48H72a8,8,0,0,1,0-16H216A8,8,0,0,1,224,40Z`}))],[`thin`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M184,68H40a4,4,0,0,0-4,4V216a4,4,0,0,0,4,4H184a4,4,0,0,0,4-4V72A4,4,0,0,0,184,68Zm-4,144H44V76H180ZM220,40V184a4,4,0,0,1-8,0V44H72a4,4,0,0,1,0-8H216A4,4,0,0,1,220,40Z`}))]]),C=new Map([[`bold`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M212.62,75.17A63.7,63.7,0,0,0,206.39,26,12,12,0,0,0,196,20a63.71,63.71,0,0,0-50,24H126A63.71,63.71,0,0,0,76,20a12,12,0,0,0-10.39,6,63.7,63.7,0,0,0-6.23,49.17A61.5,61.5,0,0,0,52,104v8a60.1,60.1,0,0,0,45.76,58.28A43.66,43.66,0,0,0,92,192v4H76a20,20,0,0,1-20-20,44.05,44.05,0,0,0-44-44,12,12,0,0,0,0,24,20,20,0,0,1,20,20,44.05,44.05,0,0,0,44,44H92v12a12,12,0,0,0,24,0V192a20,20,0,0,1,40,0v40a12,12,0,0,0,24,0V192a43.66,43.66,0,0,0-5.76-21.72A60.1,60.1,0,0,0,220,112v-8A61.5,61.5,0,0,0,212.62,75.17ZM196,112a36,36,0,0,1-36,36H112a36,36,0,0,1-36-36v-8a37.87,37.87,0,0,1,6.13-20.12,11.65,11.65,0,0,0,1.58-11.49,39.9,39.9,0,0,1-.4-27.72,39.87,39.87,0,0,1,26.41,17.8A12,12,0,0,0,119.82,68h32.35a12,12,0,0,0,10.11-5.53,39.84,39.84,0,0,1,26.41-17.8,39.9,39.9,0,0,1-.4,27.72,12,12,0,0,0,1.61,11.53A37.85,37.85,0,0,1,196,104Z`}))],[`duotone`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M208,104v8a48,48,0,0,1-48,48H136a32,32,0,0,1,32,32v40H104V192a32,32,0,0,1,32-32H112a48,48,0,0,1-48-48v-8a49.28,49.28,0,0,1,8.51-27.3A51.92,51.92,0,0,1,76,32a52,52,0,0,1,43.83,24h32.34A52,52,0,0,1,196,32a51.92,51.92,0,0,1,3.49,44.7A49.28,49.28,0,0,1,208,104Z`,opacity:`0.2`}),_.createElement(`path`,{d:`M208.3,75.68A59.74,59.74,0,0,0,202.93,28,8,8,0,0,0,196,24a59.75,59.75,0,0,0-48,24H124A59.75,59.75,0,0,0,76,24a8,8,0,0,0-6.93,4,59.78,59.78,0,0,0-5.38,47.68A58.14,58.14,0,0,0,56,104v8a56.06,56.06,0,0,0,48.44,55.47A39.8,39.8,0,0,0,96,192v8H72a24,24,0,0,1-24-24A40,40,0,0,0,8,136a8,8,0,0,0,0,16,24,24,0,0,1,24,24,40,40,0,0,0,40,40H96v16a8,8,0,0,0,16,0V192a24,24,0,0,1,48,0v40a8,8,0,0,0,16,0V192a39.8,39.8,0,0,0-8.44-24.53A56.06,56.06,0,0,0,216,112v-8A58,58,0,0,0,208.3,75.68ZM200,112a40,40,0,0,1-40,40H112a40,40,0,0,1-40-40v-8a41.74,41.74,0,0,1,6.9-22.48A8,8,0,0,0,80,73.83a43.81,43.81,0,0,1,.79-33.58,43.88,43.88,0,0,1,32.32,20.06A8,8,0,0,0,119.82,64h32.35a8,8,0,0,0,6.74-3.69,43.87,43.87,0,0,1,32.32-20.06A43.81,43.81,0,0,1,192,73.83a8.09,8.09,0,0,0,1,7.65A41.76,41.76,0,0,1,200,104Z`}))],[`fill`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M216,104v8a56.06,56.06,0,0,1-48.44,55.47A39.8,39.8,0,0,1,176,192v40a8,8,0,0,1-8,8H104a8,8,0,0,1-8-8V216H72a40,40,0,0,1-40-40A24,24,0,0,0,8,152a8,8,0,0,1,0-16,40,40,0,0,1,40,40,24,24,0,0,0,24,24H96v-8a39.8,39.8,0,0,1,8.44-24.53A56.06,56.06,0,0,1,56,112v-8a58.14,58.14,0,0,1,7.69-28.32A59.78,59.78,0,0,1,69.07,28,8,8,0,0,1,76,24a59.75,59.75,0,0,1,48,24h24a59.75,59.75,0,0,1,48-24,8,8,0,0,1,6.93,4,59.74,59.74,0,0,1,5.37,47.68A58,58,0,0,1,216,104Z`}))],[`light`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M206.13,75.92A57.79,57.79,0,0,0,201.2,29a6,6,0,0,0-5.2-3,57.77,57.77,0,0,0-47,24H123A57.77,57.77,0,0,0,76,26a6,6,0,0,0-5.2,3,57.79,57.79,0,0,0-4.93,46.92A55.88,55.88,0,0,0,58,104v8a54.06,54.06,0,0,0,50.45,53.87A37.85,37.85,0,0,0,98,192v10H72a26,26,0,0,1-26-26A38,38,0,0,0,8,138a6,6,0,0,0,0,12,26,26,0,0,1,26,26,38,38,0,0,0,38,38H98v18a6,6,0,0,0,12,0V192a26,26,0,0,1,52,0v40a6,6,0,0,0,12,0V192a37.85,37.85,0,0,0-10.45-26.13A54.06,54.06,0,0,0,214,112v-8A55.88,55.88,0,0,0,206.13,75.92ZM202,112a42,42,0,0,1-42,42H112a42,42,0,0,1-42-42v-8a43.86,43.86,0,0,1,7.3-23.69,6,6,0,0,0,.81-5.76,45.85,45.85,0,0,1,1.43-36.42,45.85,45.85,0,0,1,35.23,21.1A6,6,0,0,0,119.83,62h32.34a6,6,0,0,0,5.06-2.76,45.83,45.83,0,0,1,35.23-21.11,45.85,45.85,0,0,1,1.43,36.42,6,6,0,0,0,.79,5.74A43.78,43.78,0,0,1,202,104Z`}))],[`regular`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M208.31,75.68A59.78,59.78,0,0,0,202.93,28,8,8,0,0,0,196,24a59.75,59.75,0,0,0-48,24H124A59.75,59.75,0,0,0,76,24a8,8,0,0,0-6.93,4,59.78,59.78,0,0,0-5.38,47.68A58.14,58.14,0,0,0,56,104v8a56.06,56.06,0,0,0,48.44,55.47A39.8,39.8,0,0,0,96,192v8H72a24,24,0,0,1-24-24A40,40,0,0,0,8,136a8,8,0,0,0,0,16,24,24,0,0,1,24,24,40,40,0,0,0,40,40H96v16a8,8,0,0,0,16,0V192a24,24,0,0,1,48,0v40a8,8,0,0,0,16,0V192a39.8,39.8,0,0,0-8.44-24.53A56.06,56.06,0,0,0,216,112v-8A58.14,58.14,0,0,0,208.31,75.68ZM200,112a40,40,0,0,1-40,40H112a40,40,0,0,1-40-40v-8a41.74,41.74,0,0,1,6.9-22.48A8,8,0,0,0,80,73.83a43.81,43.81,0,0,1,.79-33.58,43.88,43.88,0,0,1,32.32,20.06A8,8,0,0,0,119.82,64h32.35a8,8,0,0,0,6.74-3.69,43.87,43.87,0,0,1,32.32-20.06A43.81,43.81,0,0,1,192,73.83a8.09,8.09,0,0,0,1,7.65A41.72,41.72,0,0,1,200,104Z`}))],[`thin`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M203.94,76.16A55.73,55.73,0,0,0,199.46,30,4,4,0,0,0,196,28a55.78,55.78,0,0,0-46,24H122A55.78,55.78,0,0,0,76,28a4,4,0,0,0-3.46,2,55.73,55.73,0,0,0-4.48,46.16A53.78,53.78,0,0,0,60,104v8a52.06,52.06,0,0,0,52,52h1.41A36,36,0,0,0,100,192v12H72a28,28,0,0,1-28-28A36,36,0,0,0,8,140a4,4,0,0,0,0,8,28,28,0,0,1,28,28,36,36,0,0,0,36,36h28v20a4,4,0,0,0,8,0V192a28,28,0,0,1,56,0v40a4,4,0,0,0,8,0V192a36,36,0,0,0-13.41-28H160a52.06,52.06,0,0,0,52-52v-8A53.78,53.78,0,0,0,203.94,76.16ZM204,112a44.05,44.05,0,0,1-44,44H112a44.05,44.05,0,0,1-44-44v-8a45.76,45.76,0,0,1,7.71-24.89,4,4,0,0,0,.53-3.84,47.82,47.82,0,0,1,2.1-39.21,47.8,47.8,0,0,1,38.12,22.1A4,4,0,0,0,119.83,60h32.34a4,4,0,0,0,3.37-1.84,47.8,47.8,0,0,1,38.12-22.1,47.82,47.82,0,0,1,2.1,39.21,4,4,0,0,0,.53,3.83A45.85,45.85,0,0,1,204,104Z`}))]]),w=new Map([[`bold`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M144,180a16,16,0,1,1-16-16A16,16,0,0,1,144,180Zm92-52A108,108,0,1,1,128,20,108.12,108.12,0,0,1,236,128Zm-24,0a84,84,0,1,0-84,84A84.09,84.09,0,0,0,212,128ZM128,64c-24.26,0-44,17.94-44,40v4a12,12,0,0,0,24,0v-4c0-8.82,9-16,20-16s20,7.18,20,16-9,16-20,16a12,12,0,0,0-12,12v8a12,12,0,0,0,23.73,2.56C158.31,137.88,172,122.37,172,104,172,81.94,152.26,64,128,64Z`}))],[`duotone`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M224,128a96,96,0,1,1-96-96A96,96,0,0,1,224,128Z`,opacity:`0.2`}),_.createElement(`path`,{d:`M140,180a12,12,0,1,1-12-12A12,12,0,0,1,140,180ZM128,72c-22.06,0-40,16.15-40,36v4a8,8,0,0,0,16,0v-4c0-11,10.77-20,24-20s24,9,24,20-10.77,20-24,20a8,8,0,0,0-8,8v8a8,8,0,0,0,16,0v-.72c18.24-3.35,32-17.9,32-35.28C168,88.15,150.06,72,128,72Zm104,56A104,104,0,1,1,128,24,104.11,104.11,0,0,1,232,128Zm-16,0a88,88,0,1,0-88,88A88.1,88.1,0,0,0,216,128Z`}))],[`fill`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm0,168a12,12,0,1,1,12-12A12,12,0,0,1,128,192Zm8-48.72V144a8,8,0,0,1-16,0v-8a8,8,0,0,1,8-8c13.23,0,24-9,24-20s-10.77-20-24-20-24,9-24,20v4a8,8,0,0,1-16,0v-4c0-19.85,17.94-36,40-36s40,16.15,40,36C168,125.38,154.24,139.93,136,143.28Z`}))],[`light`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M138,180a10,10,0,1,1-10-10A10,10,0,0,1,138,180ZM128,74c-21,0-38,15.25-38,34v4a6,6,0,0,0,12,0v-4c0-12.13,11.66-22,26-22s26,9.87,26,22-11.66,22-26,22a6,6,0,0,0-6,6v8a6,6,0,0,0,12,0v-2.42c18.11-2.58,32-16.66,32-33.58C166,89.25,149,74,128,74Zm102,54A102,102,0,1,1,128,26,102.12,102.12,0,0,1,230,128Zm-12,0a90,90,0,1,0-90,90A90.1,90.1,0,0,0,218,128Z`}))],[`regular`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M140,180a12,12,0,1,1-12-12A12,12,0,0,1,140,180ZM128,72c-22.06,0-40,16.15-40,36v4a8,8,0,0,0,16,0v-4c0-11,10.77-20,24-20s24,9,24,20-10.77,20-24,20a8,8,0,0,0-8,8v8a8,8,0,0,0,16,0v-.72c18.24-3.35,32-17.9,32-35.28C168,88.15,150.06,72,128,72Zm104,56A104,104,0,1,1,128,24,104.11,104.11,0,0,1,232,128Zm-16,0a88,88,0,1,0-88,88A88.1,88.1,0,0,0,216,128Z`}))],[`thin`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M136,180a8,8,0,1,1-8-8A8,8,0,0,1,136,180ZM128,76c-19.85,0-36,14.36-36,32v4a4,4,0,0,0,8,0v-4c0-13.23,12.56-24,28-24s28,10.77,28,24-12.56,24-28,24a4,4,0,0,0-4,4v8a4,4,0,0,0,8,0v-4.2c18-1.77,32-15.36,32-31.8C164,90.36,147.85,76,128,76Zm100,52A100,100,0,1,1,128,28,100.11,100.11,0,0,1,228,128Zm-8,0a92,92,0,1,0-92,92A92.1,92.1,0,0,0,220,128Z`}))]]),T=new Map([[`bold`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M208.49,191.51a12,12,0,0,1-17,17L128,145,64.49,208.49a12,12,0,0,1-17-17L111,128,47.51,64.49a12,12,0,0,1,17-17L128,111l63.51-63.52a12,12,0,0,1,17,17L145,128Z`}))],[`duotone`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M216,56V200a16,16,0,0,1-16,16H56a16,16,0,0,1-16-16V56A16,16,0,0,1,56,40H200A16,16,0,0,1,216,56Z`,opacity:`0.2`}),_.createElement(`path`,{d:`M205.66,194.34a8,8,0,0,1-11.32,11.32L128,139.31,61.66,205.66a8,8,0,0,1-11.32-11.32L116.69,128,50.34,61.66A8,8,0,0,1,61.66,50.34L128,116.69l66.34-66.35a8,8,0,0,1,11.32,11.32L139.31,128Z`}))],[`fill`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M208,32H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM181.66,170.34a8,8,0,0,1-11.32,11.32L128,139.31,85.66,181.66a8,8,0,0,1-11.32-11.32L116.69,128,74.34,85.66A8,8,0,0,1,85.66,74.34L128,116.69l42.34-42.35a8,8,0,0,1,11.32,11.32L139.31,128Z`}))],[`light`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M204.24,195.76a6,6,0,1,1-8.48,8.48L128,136.49,60.24,204.24a6,6,0,0,1-8.48-8.48L119.51,128,51.76,60.24a6,6,0,0,1,8.48-8.48L128,119.51l67.76-67.75a6,6,0,0,1,8.48,8.48L136.49,128Z`}))],[`regular`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M205.66,194.34a8,8,0,0,1-11.32,11.32L128,139.31,61.66,205.66a8,8,0,0,1-11.32-11.32L116.69,128,50.34,61.66A8,8,0,0,1,61.66,50.34L128,116.69l66.34-66.35a8,8,0,0,1,11.32,11.32L139.31,128Z`}))],[`thin`,_.createElement(_.Fragment,null,_.createElement(`path`,{d:`M202.83,197.17a4,4,0,0,1-5.66,5.66L128,133.66,58.83,202.83a4,4,0,0,1-5.66-5.66L122.34,128,53.17,58.83a4,4,0,0,1,5.66-5.66L128,122.34l69.17-69.17a4,4,0,1,1,5.66,5.66L133.66,128Z`}))]]),E=(0,_.createContext)({color:`currentColor`,size:`1em`,weight:`regular`,mirrored:!1}),D=_.forwardRef((e,t)=>{let{alt:n,color:r,size:i,weight:a,mirrored:o,children:s,weights:c,...l}=e,{color:u=`currentColor`,size:d,weight:f=`regular`,mirrored:p=!1,...m}=_.useContext(E);return _.createElement(`svg`,{ref:t,xmlns:`http://www.w3.org/2000/svg`,width:i??d,height:i??d,fill:r??u,viewBox:`0 0 256 256`,transform:o||p?`scale(-1, 1)`:void 0,...m,...l},!!n&&_.createElement(`title`,null,n),s,c.get(a??f))});D.displayName=`IconBase`;var O=_.forwardRef((e,t)=>_.createElement(D,{ref:t,...e,weights:v}));O.displayName=`ArrowCounterClockwiseIcon`;var k=_.forwardRef((e,t)=>_.createElement(D,{ref:t,...e,weights:y}));k.displayName=`CaretDownIcon`;var A=_.forwardRef((e,t)=>_.createElement(D,{ref:t,...e,weights:b}));A.displayName=`CheckIcon`;var j=_.forwardRef((e,t)=>_.createElement(D,{ref:t,...e,weights:x}));j.displayName=`CodeIcon`;var M=_.forwardRef((e,t)=>_.createElement(D,{ref:t,...e,weights:S}));M.displayName=`CopySimpleIcon`;var N=_.forwardRef((e,t)=>_.createElement(D,{ref:t,...e,weights:C}));N.displayName=`GithubLogoIcon`;var P=_.forwardRef((e,t)=>_.createElement(D,{ref:t,...e,weights:w}));P.displayName=`QuestionIcon`;var F=_.forwardRef((e,t)=>_.createElement(D,{ref:t,...e,weights:T}));F.displayName=`XIcon`;function I(){return typeof window<`u`}function L(e){return B(e)?(e.nodeName||``).toLowerCase():`#document`}function R(e){var t;return(e==null||(t=e.ownerDocument)==null?void 0:t.defaultView)||window}function z(e){return((B(e)?e.ownerDocument:e.document)||window.document)?.documentElement}function B(e){return I()?e instanceof Node||e instanceof R(e).Node:!1}function V(e){return I()?e instanceof Element||e instanceof R(e).Element:!1}function H(e){return I()?e instanceof HTMLElement||e instanceof R(e).HTMLElement:!1}function U(e){return!I()||typeof ShadowRoot>`u`?!1:e instanceof ShadowRoot||e instanceof R(e).ShadowRoot}function W(e){let{overflow:t,overflowX:n,overflowY:r,display:i}=le(e);return/auto|scroll|overlay|hidden|clip/.test(t+r+n)&&i!==`inline`&&i!==`contents`}function ee(e){return/^(table|td|th)$/.test(L(e))}function te(e){try{if(e.matches(`:popover-open`))return!0}catch{}try{return e.matches(`:modal`)}catch{return!1}}var G=/transform|translate|scale|rotate|perspective|filter/,ne=/paint|layout|strict|content/,re=e=>!!e&&e!==`none`,ie;function ae(e){let t=V(e)?le(e):e;return re(t.transform)||re(t.translate)||re(t.scale)||re(t.rotate)||re(t.perspective)||!se()&&(re(t.backdropFilter)||re(t.filter))||G.test(t.willChange||``)||ne.test(t.contain||``)}function oe(e){let t=de(e);for(;H(t)&&!ce(t);){if(ae(t))return t;if(te(t))return null;t=de(t)}return null}function se(){return ie??=typeof CSS<`u`&&CSS.supports&&CSS.supports(`-webkit-backdrop-filter`,`none`),ie}function ce(e){return/^(html|body|#document)$/.test(L(e))}function le(e){return R(e).getComputedStyle(e)}function ue(e){return V(e)?{scrollLeft:e.scrollLeft,scrollTop:e.scrollTop}:{scrollLeft:e.scrollX,scrollTop:e.scrollY}}function de(e){if(L(e)===`html`)return e;let t=e.assignedSlot||e.parentNode||U(e)&&e.host||z(e);return U(t)?t.host:t}function fe(e){let t=de(e);return ce(t)?(e.ownerDocument||e).body:H(t)&&W(t)?t:fe(t)}function pe(e,t,n){t===void 0&&(t=[]),n===void 0&&(n=!0);let r=fe(e),i=r===e.ownerDocument?.body,a=R(r);if(i){let e=me(a);return t.concat(a,a.visualViewport||[],W(r)?r:[],e&&n?pe(e):[])}return t.concat(r,pe(r,[],n))}function me(e){return e.parent&&Object.getPrototypeOf(e.parent)?e.frameElement:null}var he={..._},ge={};function _e(e,t){let n=_.useRef(ge);return n.current===ge&&(n.current=e(t)),n}var ve=he.useInsertionEffect,ye=ve&&ve!==he.useLayoutEffect?ve:e=>e();function K(e){let t=_e(be).current;return t.next=e,ye(t.effect),t.trampoline}function be(){let e={next:void 0,callback:xe,trampoline:(...t)=>e.callback?.(...t),effect:()=>{e.callback=e.next}};return e}function xe(){}var q=typeof document<`u`?_.useLayoutEffect:()=>{};function Se(e,t){if(e&&!t)return e;if(!e&&t)return t;if(e||t)return{...e,...t}}var Ce={};function we(e,t,n,r,i){if(!n&&!r&&!i&&!e)return Ee(t);let a=Ee(e);return t&&(a=De(a,t)),n&&(a=De(a,n)),r&&(a=De(a,r)),i&&(a=De(a,i)),a}function Te(e){if(e.length===0)return Ce;if(e.length===1)return Ee(e[0]);let t=Ee(e[0]);for(let n=1;n<e.length;n+=1)t=De(t,e[n]);return t}function Ee(e){return je(e)?{...Me(e,Ce)}:Oe(e)}function De(e,t){return je(t)?Me(t,e):ke(e,t)}function Oe(e){let t={...e};for(let e in t){let n=t[e];Ae(e,n)&&(t[e]=Pe(n))}return t}function ke(e,t){if(!t)return e;for(let n in t){let r=t[n];switch(n){case`style`:e[n]=Se(e.style,r);break;case`className`:e[n]=Ie(e.className,r);break;default:e[n]=Ae(n,r)?Ne(e[n],r):r}}return e}function Ae(e,t){let n=e.charCodeAt(0),r=e.charCodeAt(1),i=e.charCodeAt(2);return n===111&&r===110&&i>=65&&i<=90&&(typeof t==`function`||t===void 0)}function je(e){return typeof e==`function`}function Me(e,t){return je(e)?e(t):e??Ce}function Ne(e,t){return t?e?(...n)=>{let r=n[0];if(Le(r)){let i=r;Fe(i);let a=t(...n);return i.baseUIHandlerPrevented||e?.(...n),a}let i=t(...n);return e?.(...n),i}:Pe(t):e}function Pe(e){return e&&((...t)=>{let n=t[0];return Le(n)&&Fe(n),e(...t)})}function Fe(e){return e.preventBaseUIHandler=()=>{e.baseUIHandlerPrevented=!0},e}function Ie(e,t){return t?e?t+` `+e:t:e}function Le(e){return typeof e==`object`&&!!e&&`nativeEvent`in e}function Re(e,t){return function(n,...r){let i=new URL(e);return i.searchParams.set(`code`,n.toString()),r.forEach(e=>i.searchParams.append(`args[]`,e)),`${t} error #${n}; visit ${i} for the full message.`}}var ze=Re(`https://base-ui.com/production-error`,`Base UI`),Be=_.createContext(void 0);function Ve(e=!1){let t=_.useContext(Be);if(t===void 0&&!e)throw Error(ze(16));return t}function He(e){let{focusableWhenDisabled:t,disabled:n,composite:r=!1,tabIndex:i=0,isNativeButton:a}=e,o=r&&t!==!1,s=r&&t===!1;return{props:_.useMemo(()=>{let e={onKeyDown(e){n&&t&&e.key!==`Tab`&&e.preventDefault()}};return r||(e.tabIndex=i,!a&&n&&(e.tabIndex=t?i:-1)),(a&&(t||o)||!a&&n)&&(e[`aria-disabled`]=n),a&&(!t||s)&&(e.disabled=n),e},[r,n,t,o,s,a,i])}}function Ue(e){return e?.ownerDocument||document}function We(e,t,{detail:n=0}={}){e.dispatchEvent(new(R(e)).PointerEvent(`click`,{bubbles:!0,cancelable:!0,composed:!0,detail:n,shiftKey:t.shiftKey,ctrlKey:t.ctrlKey,altKey:t.altKey,metaKey:t.metaKey}))}function Ge(e={}){let{disabled:t=!1,focusableWhenDisabled:n,tabIndex:r=0,native:i=!0,composite:a}=e,o=_.useRef(null),s=Ve(!0),c=a??s!==void 0,{props:l}=He({focusableWhenDisabled:n,disabled:t,composite:c,tabIndex:r,isNativeButton:i}),u=_.useCallback(()=>{let e=o.current;Ke(e)&&c&&t&&l.disabled===void 0&&e.disabled&&(e.disabled=!1)},[t,l.disabled,c]);return q(u,[u]),{getButtonProps:_.useCallback((e={})=>{let{onClick:n,onMouseDown:r,onKeyUp:a,onKeyDown:o,onPointerDown:s,...u}=e;return we({onClick(e){if(t){e.preventDefault();return}n?.(e)},onMouseDown(e){t||r?.(e)},onKeyDown(e){if(t||(Fe(e),o?.(e),e.baseUIHandlerPrevented))return;let n=e.target===e.currentTarget,r=e.currentTarget,a=Ke(r),s=!i&&qe(r),l=n&&(i?a:!s),u=e.key===`Enter`,d=e.key===` `,f=r.getAttribute(`role`),p=f?.startsWith(`menuitem`)||f===`option`||f===`gridcell`;if(n&&c&&d){if(e.defaultPrevented&&p)return;e.preventDefault(),(!i||a)&&(e.preventBaseUIHandler(),We(r,e));return}if(!l||i||!d&&!u){n&&s&&d&&e.preventDefault();return}e.defaultPrevented||(e.preventDefault(),u&&(e.preventBaseUIHandler(),We(r,e)))},onKeyUp(e){if(!t){if(Fe(e),a?.(e),e.target===e.currentTarget&&i&&c&&Ke(e.currentTarget)&&e.key===` `){e.preventDefault();return}e.baseUIHandlerPrevented||e.target===e.currentTarget&&!i&&!c&&!e.defaultPrevented&&e.key===` `&&(e.preventBaseUIHandler(),We(e.currentTarget,e))}},onPointerDown(e){if(t){e.preventDefault();return}s?.(e)}},i?{type:`button`}:{role:`button`},l,u)},[t,l,c,i]),buttonRef:K(e=>{o.current=e,u()})}}function Ke(e){return H(e)&&e.tagName===`BUTTON`}function qe(e){return H(e)&&e.tagName===`A`&&!!e.href}function Je(e,t,n,r){let i=_e(Xe).current;return Ze(i,e,t,n,r)&&$e(i,[e,t,n,r]),i.callback}function Ye(e){let t=_e(Xe).current;return Qe(t,e)&&$e(t,e),t.callback}function Xe(){return{callback:null,cleanup:null,refs:[]}}function Ze(e,t,n,r,i){return e.refs[0]!==t||e.refs[1]!==n||e.refs[2]!==r||e.refs[3]!==i}function Qe(e,t){return e.refs.length!==t.length||e.refs.some((e,n)=>e!==t[n])}function $e(e,t){if(e.refs=t,t.every(e=>e==null)){e.callback=null;return}e.callback=n=>{if(e.cleanup&&=(e.cleanup(),null),n!=null){let r=Array(t.length).fill(null);for(let e=0;e<t.length;e+=1){let i=t[e];if(i!=null)switch(typeof i){case`function`:{let t=i(n);typeof t==`function`&&(r[e]=t);break}case`object`:i.current=n}}e.cleanup=()=>{for(let e=0;e<t.length;e+=1){let n=t[e];if(n!=null)switch(typeof n){case`function`:{let t=r[e];typeof t==`function`?t():n(null);break}case`object`:n.current=null}}}}}}var et=19;function tt(e){return et>=e}function nt(e){if(!_.isValidElement(e))return null;let t=e,n=t.props;return(tt(19)?n?.ref:t.ref)??null}function rt(){}var it=Object.freeze([]),at=Object.freeze({});function ot(e,t){let n={};for(let r in e){let i=e[r];if(t?.hasOwnProperty(r)){let e=t[r](i);e!=null&&Object.assign(n,e);continue}i===!0?n[`data-${r.toLowerCase()}`]=``:i&&(n[`data-${r.toLowerCase()}`]=i.toString())}return n}function st(e,t){return typeof e==`function`?e(t):e}function ct(e,t){return typeof e==`function`?e(t):e}function lt(e,t,n={}){let r=t.render,i=ut(t,n);return n.enabled===!1?null:pt(e,r,i,n.state??at)}function ut(e,t={}){let{className:n,style:r,render:i}=e,{state:a=at,ref:o,props:s,stateAttributesMapping:c,enabled:l=!0}=t,u=l?st(n,a):void 0,d=l?ct(r,a):void 0,f=l?ot(a,c):at,p=l&&s?dt(s):void 0,m=l?Se(f,p)??{}:at;return typeof document<`u`&&(l?m.ref=Array.isArray(o)?Ye([m.ref,nt(i),...o]):Je(m.ref,nt(i),o):Je(null,null)),l?(u!==void 0&&(m.className=Ie(m.className,u)),d!==void 0&&(m.style=Se(m.style,d)),m):at}function dt(e){return Array.isArray(e)?Te(e):we(void 0,e)}var ft=Symbol.for(`react.lazy`);function pt(e,t,n,r){if(t){if(typeof t==`function`)return t(n,r);let e=we(n,t.props);e.ref=n.ref;let i=t;return i?.$$typeof===ft&&(i=_.Children.toArray(t)[0]),_.cloneElement(i,e)}if(e&&typeof e==`string`)return mt(e,n);throw Error(ze(8))}function mt(e,t){return e===`button`?(0,_.createElement)(`button`,{type:`button`,...t,key:t.key}):e===`img`?(0,_.createElement)(`img`,{alt:``,...t,key:t.key}):_.createElement(e,t)}var ht=_.forwardRef(function(e,t){let{render:n,className:r,disabled:i=!1,focusableWhenDisabled:a=!1,nativeButton:o=!0,style:s,...c}=e,{getButtonProps:l,buttonRef:u}=Ge({disabled:i,focusableWhenDisabled:a,native:o});return lt(`button`,e,{state:{disabled:i},ref:[t,u],props:[c,l]})}),gt=g();function _t(e){var t,n,r=``;if(typeof e==`string`||typeof e==`number`)r+=e;else if(typeof e==`object`){if(Array.isArray(e)){var i=e.length;for(t=0;t<i;t++)e[t]&&(n=_t(e[t]))&&(r&&(r+=` `),r+=n)}else for(n in e)e[n]&&(r&&(r+=` `),r+=n)}return r}function vt(){for(var e,t,n=0,r=``,i=arguments.length;n<i;n++)(e=arguments[n])&&(t=_t(e))&&(r&&(r+=` `),r+=t);return r}var yt=e=>typeof e==`boolean`?`${e}`:e===0?`0`:e,bt=vt,xt=(e,t)=>n=>{if(t?.variants==null)return bt(e,n?.class,n?.className);let{variants:r,defaultVariants:i}=t,a=Object.keys(r).map(e=>{let t=n?.[e],a=i?.[e];if(t===null)return null;let o=yt(t)||yt(a);return r[e][o]}),o=n&&Object.entries(n).reduce((e,t)=>{let[n,r]=t;return r===void 0||(e[n]=r),e},{});return bt(e,a,t?.compoundVariants?.reduce((e,t)=>{let{class:n,className:r,...a}=t;return Object.entries(a).every(e=>{let[t,n]=e;return Array.isArray(n)?n.includes({...i,...o}[t]):{...i,...o}[t]===n})?[...e,n,r]:e},[]),n?.class,n?.className)},St=(e,t)=>{let n=Array(e.length+t.length);for(let t=0;t<e.length;t++)n[t]=e[t];for(let r=0;r<t.length;r++)n[e.length+r]=t[r];return n},Ct=(e,t)=>({classGroupId:e,validator:t}),wt=(e=new Map,t=null,n)=>({nextPart:e,validators:t,classGroupId:n}),Tt=`-`,Et=[],Dt=`arbitrary..`,Ot=e=>{let t=jt(e),{conflictingClassGroups:n,conflictingClassGroupModifiers:r}=e;return{getClassGroupId:e=>{if(e.startsWith(`[`)&&e.endsWith(`]`))return At(e);let n=e.split(Tt);return kt(n,+(n[0]===``&&n.length>1),t)},getConflictingClassGroupIds:(e,t)=>{if(t){let t=r[e],i=n[e];return t?i?St(i,t):t:i||Et}return n[e]||Et}}},kt=(e,t,n)=>{if(e.length-t===0)return n.classGroupId;let r=e[t],i=n.nextPart.get(r);if(i){let n=kt(e,t+1,i);if(n)return n}let a=n.validators;if(a===null)return;let o=t===0?e.join(Tt):e.slice(t).join(Tt),s=a.length;for(let e=0;e<s;e++){let t=a[e];if(t.validator(o))return t.classGroupId}},At=e=>e.slice(1,-1).indexOf(`:`)===-1?void 0:(()=>{let t=e.slice(1,-1),n=t.indexOf(`:`),r=t.slice(0,n);return r?Dt+r:void 0})(),jt=e=>{let{theme:t,classGroups:n}=e;return Mt(n,t)},Mt=(e,t)=>{let n=wt();for(let r in e){let i=e[r];Nt(i,n,r,t)}return n},Nt=(e,t,n,r)=>{let i=e.length;for(let a=0;a<i;a++){let i=e[a];Pt(i,t,n,r)}},Pt=(e,t,n,r)=>{if(typeof e==`string`){Ft(e,t,n);return}if(typeof e==`function`){It(e,t,n,r);return}Lt(e,t,n,r)},Ft=(e,t,n)=>{let r=e===``?t:Rt(t,e);r.classGroupId=n},It=(e,t,n,r)=>{if(zt(e)){Nt(e(r),t,n,r);return}t.validators===null&&(t.validators=[]),t.validators.push(Ct(n,e))},Lt=(e,t,n,r)=>{let i=Object.entries(e),a=i.length;for(let e=0;e<a;e++){let[a,o]=i[e];Nt(o,Rt(t,a),n,r)}},Rt=(e,t)=>{let n=e,r=t.split(Tt),i=r.length;for(let e=0;e<i;e++){let t=r[e],i=n.nextPart.get(t);i||(i=wt(),n.nextPart.set(t,i)),n=i}return n},zt=e=>`isThemeGetter`in e&&e.isThemeGetter===!0,Bt=e=>{if(e<1)return{get:()=>void 0,set:()=>{}};let t=0,n=Object.create(null),r=Object.create(null),i=(i,a)=>{n[i]=a,t++,t>e&&(t=0,r=n,n=Object.create(null))};return{get(e){let t=n[e];if(t!==void 0)return t;if((t=r[e])!==void 0)return i(e,t),t},set(e,t){e in n?n[e]=t:i(e,t)}}},Vt=`!`,Ht=`:`,Ut=[],Wt=(e,t,n,r,i)=>({modifiers:e,hasImportantModifier:t,baseClassName:n,maybePostfixModifierPosition:r,isExternal:i}),Gt=e=>{let{prefix:t,experimentalParseClassName:n}=e,r=e=>{let t=[],n=0,r=0,i=0,a,o=e.length;for(let s=0;s<o;s++){let o=e[s];if(n===0&&r===0){if(o===Ht){t.push(e.slice(i,s)),i=s+1;continue}if(o===`/`){a=s;continue}}o===`[`?n++:o===`]`?n--:o===`(`?r++:o===`)`&&r--}let s=t.length===0?e:e.slice(i),c=s,l=!1;s.endsWith(Vt)?(c=s.slice(0,-1),l=!0):s.startsWith(Vt)&&(c=s.slice(1),l=!0);let u=a&&a>i?a-i:void 0;return Wt(t,l,c,u)};if(t){let e=t+Ht,n=r;r=t=>t.startsWith(e)?n(t.slice(e.length)):Wt(Ut,!1,t,void 0,!0)}if(n){let e=r;r=t=>n({className:t,parseClassName:e})}return r},Kt=e=>{let t=new Map;return e.orderSensitiveModifiers.forEach((e,n)=>{t.set(e,1e6+n)}),e=>{let n=[],r=[];for(let i=0;i<e.length;i++){let a=e[i],o=a[0]===`[`,s=t.has(a);o||s?(r.length>0&&(r.sort(),n.push(...r),r=[]),n.push(a)):r.push(a)}return r.length>0&&(r.sort(),n.push(...r)),n}},qt=e=>({cache:Bt(e.cacheSize),parseClassName:Gt(e),sortModifiers:Kt(e),postfixLookupClassGroupIds:Jt(e),...Ot(e)}),Jt=e=>{let t=Object.create(null),n=e.postfixLookupClassGroups;if(n)for(let e=0;e<n.length;e++)t[n[e]]=!0;return t},Yt=/\s+/,Xt=(e,t)=>{let{parseClassName:n,getClassGroupId:r,getConflictingClassGroupIds:i,sortModifiers:a,postfixLookupClassGroupIds:o}=t,s=[],c=e.trim().split(Yt),l=``;for(let e=c.length-1;e>=0;--e){let t=c[e],{isExternal:u,modifiers:d,hasImportantModifier:f,baseClassName:p,maybePostfixModifierPosition:m}=n(t);if(u){l=t+(l.length>0?` `+l:l);continue}let h=!!m,g;if(h){g=r(p.substring(0,m));let e=g&&o[g]?r(p):void 0;e&&e!==g&&(g=e,h=!1)}else g=r(p);if(!g){if(!h){l=t+(l.length>0?` `+l:l);continue}if(g=r(p),!g){l=t+(l.length>0?` `+l:l);continue}h=!1}let _=d.length===0?``:d.length===1?d[0]:a(d).join(`:`),v=f?_+Vt:_,y=v+g;if(s.indexOf(y)>-1)continue;s.push(y);let b=i(g,h);for(let e=0;e<b.length;++e){let t=b[e];s.push(v+t)}l=t+(l.length>0?` `+l:l)}return l},Zt=(...e)=>{let t=0,n,r,i=``;for(;t<e.length;)(n=e[t++])&&(r=Qt(n))&&(i&&(i+=` `),i+=r);return i},Qt=e=>{if(typeof e==`string`)return e;let t,n=``;for(let r=0;r<e.length;r++)e[r]&&(t=Qt(e[r]))&&(n&&(n+=` `),n+=t);return n},$t=(e,...t)=>{let n,r,i,a,o=o=>(n=qt(t.reduce((e,t)=>t(e),e())),r=n.cache.get,i=n.cache.set,a=s,s(o)),s=e=>{let t=r(e);if(t)return t;let a=Xt(e,n);return i(e,a),a};return a=o,(...e)=>a(Zt(...e))},en=[],tn=e=>{let t=t=>t[e]||en;return t.isThemeGetter=!0,t},nn=/^\[(?:(\w[\w-]*):)?(.+)\]$/i,rn=/^\((?:(\w[\w-]*):)?(.+)\)$/i,an=/^\d+(?:\.\d+)?\/\d+(?:\.\d+)?$/,on=/^(\d+(\.\d+)?)?(xs|sm|md|lg|xl)$/,sn=/\d+(%|px|r?em|[sdl]?v([hwib]|min|max)|pt|pc|in|cm|mm|cap|ch|ex|r?lh|cq(w|h|i|b|min|max))|\b(calc|min|max|clamp)\(.+\)|^0$/,cn=/^(rgba?|hsla?|hwb|(ok)?(lab|lch)|color-mix)\(.+\)$/,ln=/^(inset_)?-?((\d+)?\.?(\d+)[a-z]+|0)_-?((\d+)?\.?(\d+)[a-z]+|0)/,un=/^(url|image|image-set|cross-fade|element|(repeating-)?(linear|radial|conic)-gradient)\(.+\)$/,dn=e=>an.test(e),fn=e=>!!e&&!Number.isNaN(Number(e)),pn=e=>!!e&&Number.isInteger(Number(e)),mn=e=>e.endsWith(`%`)&&fn(e.slice(0,-1)),hn=e=>on.test(e),gn=()=>!0,_n=e=>sn.test(e)&&!cn.test(e),vn=()=>!1,yn=e=>ln.test(e),bn=e=>un.test(e),xn=e=>!J(e)&&!Y(e),Sn=e=>e.startsWith(`@container`)&&(e[10]===`/`&&e[11]!==void 0||e[11]===`s`&&e[16]!==void 0&&e.startsWith(`-size/`,10)||e[11]===`n`&&e[18]!==void 0&&e.startsWith(`-normal/`,10)),Cn=e=>Rn(e,Hn,vn),J=e=>nn.test(e),wn=e=>Rn(e,Un,_n),Tn=e=>Rn(e,Wn,fn),En=e=>Rn(e,Kn,gn),Dn=e=>Rn(e,Gn,vn),On=e=>Rn(e,Bn,vn),kn=e=>Rn(e,Vn,bn),An=e=>Rn(e,qn,yn),Y=e=>rn.test(e),jn=e=>zn(e,Un),Mn=e=>zn(e,Gn),Nn=e=>zn(e,Bn),Pn=e=>zn(e,Hn),Fn=e=>zn(e,Vn),In=e=>zn(e,qn,!0),Ln=e=>zn(e,Kn,!0),Rn=(e,t,n)=>{let r=nn.exec(e);return r?r[1]?t(r[1]):n(r[2]):!1},zn=(e,t,n=!1)=>{let r=rn.exec(e);return r?r[1]?t(r[1]):n:!1},Bn=e=>e===`position`||e===`percentage`,Vn=e=>e===`image`||e===`url`,Hn=e=>e===`length`||e===`size`||e===`bg-size`,Un=e=>e===`length`,Wn=e=>e===`number`,Gn=e=>e===`family-name`,Kn=e=>e===`number`||e===`weight`,qn=e=>e===`shadow`,Jn=$t(()=>{let e=tn(`color`),t=tn(`font`),n=tn(`text`),r=tn(`font-weight`),i=tn(`tracking`),a=tn(`leading`),o=tn(`breakpoint`),s=tn(`container`),c=tn(`spacing`),l=tn(`radius`),u=tn(`shadow`),d=tn(`inset-shadow`),f=tn(`text-shadow`),p=tn(`drop-shadow`),m=tn(`blur`),h=tn(`perspective`),g=tn(`aspect`),_=tn(`ease`),v=tn(`animate`),y=()=>[`auto`,`avoid`,`all`,`avoid-page`,`page`,`left`,`right`,`column`],b=()=>[`center`,`top`,`bottom`,`left`,`right`,`top-left`,`left-top`,`top-right`,`right-top`,`bottom-right`,`right-bottom`,`bottom-left`,`left-bottom`],x=()=>[...b(),Y,J],S=()=>[`auto`,`hidden`,`clip`,`visible`,`scroll`],C=()=>[`auto`,`contain`,`none`],w=()=>[Y,J,c],T=()=>[dn,`full`,`auto`,...w()],E=()=>[pn,`none`,`subgrid`,Y,J],D=()=>[`auto`,{span:[`full`,pn,Y,J]},pn,Y,J],O=()=>[pn,`auto`,Y,J],k=()=>[`auto`,`min`,`max`,`fr`,Y,J],A=()=>[`start`,`end`,`center`,`between`,`around`,`evenly`,`stretch`,`baseline`,`center-safe`,`end-safe`],j=()=>[`start`,`end`,`center`,`stretch`,`center-safe`,`end-safe`],M=()=>[`auto`,...w()],N=()=>[dn,`auto`,`full`,`dvw`,`dvh`,`lvw`,`lvh`,`svw`,`svh`,`min`,`max`,`fit`,...w()],P=()=>[dn,`screen`,`full`,`dvw`,`lvw`,`svw`,`min`,`max`,`fit`,...w()],F=()=>[dn,`screen`,`full`,`lh`,`dvh`,`lvh`,`svh`,`min`,`max`,`fit`,...w()],I=()=>[e,Y,J],L=()=>[...b(),Nn,On,{position:[Y,J]}],R=()=>[`no-repeat`,{repeat:[``,`x`,`y`,`space`,`round`]}],z=()=>[`auto`,`cover`,`contain`,Pn,Cn,{size:[Y,J]}],B=()=>[mn,jn,wn],V=()=>[``,`none`,`full`,l,Y,J],H=()=>[``,fn,jn,wn],U=()=>[`solid`,`dashed`,`dotted`,`double`],W=()=>[`normal`,`multiply`,`screen`,`overlay`,`darken`,`lighten`,`color-dodge`,`color-burn`,`hard-light`,`soft-light`,`difference`,`exclusion`,`hue`,`saturation`,`color`,`luminosity`],ee=()=>[fn,mn,Nn,On],te=()=>[``,`none`,m,Y,J],G=()=>[`none`,fn,Y,J],ne=()=>[`none`,fn,Y,J],re=()=>[fn,Y,J],ie=()=>[dn,`full`,...w()];return{cacheSize:500,theme:{animate:[`spin`,`ping`,`pulse`,`bounce`],aspect:[`video`],blur:[hn],breakpoint:[hn],color:[gn],container:[hn],"drop-shadow":[hn],ease:[`in`,`out`,`in-out`],font:[xn],"font-weight":[`thin`,`extralight`,`light`,`normal`,`medium`,`semibold`,`bold`,`extrabold`,`black`],"inset-shadow":[hn],leading:[`none`,`tight`,`snug`,`normal`,`relaxed`,`loose`],perspective:[`dramatic`,`near`,`normal`,`midrange`,`distant`,`none`],radius:[hn],shadow:[hn],spacing:[`px`,fn],text:[hn],"text-shadow":[hn],tracking:[`tighter`,`tight`,`normal`,`wide`,`wider`,`widest`]},classGroups:{aspect:[{aspect:[`auto`,`square`,dn,J,Y,g]}],container:[`container`],"container-type":[{"@container":[``,`normal`,`size`,Y,J]}],"container-named":[Sn],columns:[{columns:[fn,J,Y,s]}],"break-after":[{"break-after":y()}],"break-before":[{"break-before":y()}],"break-inside":[{"break-inside":[`auto`,`avoid`,`avoid-page`,`avoid-column`]}],"box-decoration":[{"box-decoration":[`slice`,`clone`]}],box:[{box:[`border`,`content`]}],display:[`block`,`inline-block`,`inline`,`flex`,`inline-flex`,`table`,`inline-table`,`table-caption`,`table-cell`,`table-column`,`table-column-group`,`table-footer-group`,`table-header-group`,`table-row-group`,`table-row`,`flow-root`,`grid`,`inline-grid`,`contents`,`list-item`,`hidden`],sr:[`sr-only`,`not-sr-only`],float:[{float:[`right`,`left`,`none`,`start`,`end`]}],clear:[{clear:[`left`,`right`,`both`,`none`,`start`,`end`]}],isolation:[`isolate`,`isolation-auto`],"object-fit":[{object:[`contain`,`cover`,`fill`,`none`,`scale-down`]}],"object-position":[{object:x()}],overflow:[{overflow:S()}],"overflow-x":[{"overflow-x":S()}],"overflow-y":[{"overflow-y":S()}],overscroll:[{overscroll:C()}],"overscroll-x":[{"overscroll-x":C()}],"overscroll-y":[{"overscroll-y":C()}],position:[`static`,`fixed`,`absolute`,`relative`,`sticky`],inset:[{inset:T()}],"inset-x":[{"inset-x":T()}],"inset-y":[{"inset-y":T()}],start:[{"inset-s":T(),start:T()}],end:[{"inset-e":T(),end:T()}],"inset-bs":[{"inset-bs":T()}],"inset-be":[{"inset-be":T()}],top:[{top:T()}],right:[{right:T()}],bottom:[{bottom:T()}],left:[{left:T()}],visibility:[`visible`,`invisible`,`collapse`],z:[{z:[pn,`auto`,Y,J]}],basis:[{basis:[dn,`full`,`auto`,s,...w()]}],"flex-direction":[{flex:[`row`,`row-reverse`,`col`,`col-reverse`]}],"flex-wrap":[{flex:[`nowrap`,`wrap`,`wrap-reverse`]}],flex:[{flex:[fn,dn,`auto`,`initial`,`none`,J]}],grow:[{grow:[``,fn,Y,J]}],shrink:[{shrink:[``,fn,Y,J]}],order:[{order:[pn,`first`,`last`,`none`,Y,J]}],"grid-cols":[{"grid-cols":E()}],"col-start-end":[{col:D()}],"col-start":[{"col-start":O()}],"col-end":[{"col-end":O()}],"grid-rows":[{"grid-rows":E()}],"row-start-end":[{row:D()}],"row-start":[{"row-start":O()}],"row-end":[{"row-end":O()}],"grid-flow":[{"grid-flow":[`row`,`col`,`dense`,`row-dense`,`col-dense`]}],"auto-cols":[{"auto-cols":k()}],"auto-rows":[{"auto-rows":k()}],gap:[{gap:w()}],"gap-x":[{"gap-x":w()}],"gap-y":[{"gap-y":w()}],"justify-content":[{justify:[...A(),`normal`]}],"justify-items":[{"justify-items":[...j(),`normal`]}],"justify-self":[{"justify-self":[`auto`,...j()]}],"align-content":[{content:[`normal`,...A()]}],"align-items":[{items:[...j(),{baseline:[``,`last`]}]}],"align-self":[{self:[`auto`,...j(),{baseline:[``,`last`]}]}],"place-content":[{"place-content":A()}],"place-items":[{"place-items":[...j(),`baseline`]}],"place-self":[{"place-self":[`auto`,...j()]}],p:[{p:w()}],px:[{px:w()}],py:[{py:w()}],ps:[{ps:w()}],pe:[{pe:w()}],pbs:[{pbs:w()}],pbe:[{pbe:w()}],pt:[{pt:w()}],pr:[{pr:w()}],pb:[{pb:w()}],pl:[{pl:w()}],m:[{m:M()}],mx:[{mx:M()}],my:[{my:M()}],ms:[{ms:M()}],me:[{me:M()}],mbs:[{mbs:M()}],mbe:[{mbe:M()}],mt:[{mt:M()}],mr:[{mr:M()}],mb:[{mb:M()}],ml:[{ml:M()}],"space-x":[{"space-x":w()}],"space-x-reverse":[`space-x-reverse`],"space-y":[{"space-y":w()}],"space-y-reverse":[`space-y-reverse`],size:[{size:N()}],"inline-size":[{inline:[`auto`,...P()]}],"min-inline-size":[{"min-inline":[`auto`,...P()]}],"max-inline-size":[{"max-inline":[`none`,...P()]}],"block-size":[{block:[`auto`,...F()]}],"min-block-size":[{"min-block":[`auto`,...F()]}],"max-block-size":[{"max-block":[`none`,...F()]}],w:[{w:[s,`screen`,...N()]}],"min-w":[{"min-w":[s,`screen`,`none`,...N()]}],"max-w":[{"max-w":[s,`screen`,`none`,`prose`,{screen:[o]},...N()]}],h:[{h:[`screen`,`lh`,...N()]}],"min-h":[{"min-h":[`screen`,`lh`,`none`,...N()]}],"max-h":[{"max-h":[`screen`,`lh`,...N()]}],"font-size":[{text:[`base`,n,jn,wn]}],"font-smoothing":[`antialiased`,`subpixel-antialiased`],"font-style":[`italic`,`not-italic`],"font-weight":[{font:[r,Ln,En]}],"font-stretch":[{"font-stretch":[`ultra-condensed`,`extra-condensed`,`condensed`,`semi-condensed`,`normal`,`semi-expanded`,`expanded`,`extra-expanded`,`ultra-expanded`,mn,J]}],"font-family":[{font:[Mn,Dn,t]}],"font-features":[{"font-features":[J]}],"fvn-normal":[`normal-nums`],"fvn-ordinal":[`ordinal`],"fvn-slashed-zero":[`slashed-zero`],"fvn-figure":[`lining-nums`,`oldstyle-nums`],"fvn-spacing":[`proportional-nums`,`tabular-nums`],"fvn-fraction":[`diagonal-fractions`,`stacked-fractions`],tracking:[{tracking:[i,Y,J]}],"line-clamp":[{"line-clamp":[fn,`none`,Y,Tn]}],leading:[{leading:[a,...w()]}],"list-image":[{"list-image":[`none`,Y,J]}],"list-style-position":[{list:[`inside`,`outside`]}],"list-style-type":[{list:[`disc`,`decimal`,`none`,Y,J]}],"text-alignment":[{text:[`left`,`center`,`right`,`justify`,`start`,`end`]}],"placeholder-color":[{placeholder:I()}],"text-color":[{text:I()}],"text-decoration":[`underline`,`overline`,`line-through`,`no-underline`],"text-decoration-style":[{decoration:[...U(),`wavy`]}],"text-decoration-thickness":[{decoration:[fn,`from-font`,`auto`,Y,wn]}],"text-decoration-color":[{decoration:I()}],"underline-offset":[{"underline-offset":[fn,`auto`,Y,J]}],"text-transform":[`uppercase`,`lowercase`,`capitalize`,`normal-case`],"text-overflow":[`truncate`,`text-ellipsis`,`text-clip`],"text-wrap":[{text:[`wrap`,`nowrap`,`balance`,`pretty`]}],indent:[{indent:w()}],"tab-size":[{tab:[pn,Y,J]}],"vertical-align":[{align:[`baseline`,`top`,`middle`,`bottom`,`text-top`,`text-bottom`,`sub`,`super`,Y,J]}],whitespace:[{whitespace:[`normal`,`nowrap`,`pre`,`pre-line`,`pre-wrap`,`break-spaces`]}],break:[{break:[`normal`,`words`,`all`,`keep`]}],wrap:[{wrap:[`break-word`,`anywhere`,`normal`]}],hyphens:[{hyphens:[`none`,`manual`,`auto`]}],content:[{content:[`none`,Y,J]}],"bg-attachment":[{bg:[`fixed`,`local`,`scroll`]}],"bg-clip":[{"bg-clip":[`border`,`padding`,`content`,`text`]}],"bg-origin":[{"bg-origin":[`border`,`padding`,`content`]}],"bg-position":[{bg:L()}],"bg-repeat":[{bg:R()}],"bg-size":[{bg:z()}],"bg-image":[{bg:[`none`,{linear:[{to:[`t`,`tr`,`r`,`br`,`b`,`bl`,`l`,`tl`]},pn,Y,J],radial:[``,Y,J],conic:[pn,Y,J]},Fn,kn]}],"bg-color":[{bg:I()}],"gradient-from-pos":[{from:B()}],"gradient-via-pos":[{via:B()}],"gradient-to-pos":[{to:B()}],"gradient-from":[{from:I()}],"gradient-via":[{via:I()}],"gradient-to":[{to:I()}],rounded:[{rounded:V()}],"rounded-s":[{"rounded-s":V()}],"rounded-e":[{"rounded-e":V()}],"rounded-t":[{"rounded-t":V()}],"rounded-r":[{"rounded-r":V()}],"rounded-b":[{"rounded-b":V()}],"rounded-l":[{"rounded-l":V()}],"rounded-ss":[{"rounded-ss":V()}],"rounded-se":[{"rounded-se":V()}],"rounded-ee":[{"rounded-ee":V()}],"rounded-es":[{"rounded-es":V()}],"rounded-tl":[{"rounded-tl":V()}],"rounded-tr":[{"rounded-tr":V()}],"rounded-br":[{"rounded-br":V()}],"rounded-bl":[{"rounded-bl":V()}],"border-w":[{border:H()}],"border-w-x":[{"border-x":H()}],"border-w-y":[{"border-y":H()}],"border-w-s":[{"border-s":H()}],"border-w-e":[{"border-e":H()}],"border-w-bs":[{"border-bs":H()}],"border-w-be":[{"border-be":H()}],"border-w-t":[{"border-t":H()}],"border-w-r":[{"border-r":H()}],"border-w-b":[{"border-b":H()}],"border-w-l":[{"border-l":H()}],"divide-x":[{"divide-x":H()}],"divide-x-reverse":[`divide-x-reverse`],"divide-y":[{"divide-y":H()}],"divide-y-reverse":[`divide-y-reverse`],"border-style":[{border:[...U(),`hidden`,`none`]}],"divide-style":[{divide:[...U(),`hidden`,`none`]}],"border-color":[{border:I()}],"border-color-x":[{"border-x":I()}],"border-color-y":[{"border-y":I()}],"border-color-s":[{"border-s":I()}],"border-color-e":[{"border-e":I()}],"border-color-bs":[{"border-bs":I()}],"border-color-be":[{"border-be":I()}],"border-color-t":[{"border-t":I()}],"border-color-r":[{"border-r":I()}],"border-color-b":[{"border-b":I()}],"border-color-l":[{"border-l":I()}],"divide-color":[{divide:I()}],"outline-style":[{outline:[...U(),`none`,`hidden`]}],"outline-offset":[{"outline-offset":[fn,Y,J]}],"outline-w":[{outline:[``,fn,jn,wn]}],"outline-color":[{outline:I()}],shadow:[{shadow:[``,`none`,u,In,An]}],"shadow-color":[{shadow:I()}],"inset-shadow":[{"inset-shadow":[`none`,d,In,An]}],"inset-shadow-color":[{"inset-shadow":I()}],"ring-w":[{ring:H()}],"ring-w-inset":[`ring-inset`],"ring-color":[{ring:I()}],"ring-offset-w":[{"ring-offset":[fn,wn]}],"ring-offset-color":[{"ring-offset":I()}],"inset-ring-w":[{"inset-ring":H()}],"inset-ring-color":[{"inset-ring":I()}],"text-shadow":[{"text-shadow":[`none`,f,In,An]}],"text-shadow-color":[{"text-shadow":I()}],opacity:[{opacity:[fn,Y,J]}],"mix-blend":[{"mix-blend":[...W(),`plus-darker`,`plus-lighter`]}],"bg-blend":[{"bg-blend":W()}],"mask-clip":[{"mask-clip":[`border`,`padding`,`content`,`fill`,`stroke`,`view`]},`mask-no-clip`],"mask-composite":[{mask:[`add`,`subtract`,`intersect`,`exclude`]}],"mask-image-linear-pos":[{"mask-linear":[fn]}],"mask-image-linear-from-pos":[{"mask-linear-from":ee()}],"mask-image-linear-to-pos":[{"mask-linear-to":ee()}],"mask-image-linear-from-color":[{"mask-linear-from":I()}],"mask-image-linear-to-color":[{"mask-linear-to":I()}],"mask-image-t-from-pos":[{"mask-t-from":ee()}],"mask-image-t-to-pos":[{"mask-t-to":ee()}],"mask-image-t-from-color":[{"mask-t-from":I()}],"mask-image-t-to-color":[{"mask-t-to":I()}],"mask-image-r-from-pos":[{"mask-r-from":ee()}],"mask-image-r-to-pos":[{"mask-r-to":ee()}],"mask-image-r-from-color":[{"mask-r-from":I()}],"mask-image-r-to-color":[{"mask-r-to":I()}],"mask-image-b-from-pos":[{"mask-b-from":ee()}],"mask-image-b-to-pos":[{"mask-b-to":ee()}],"mask-image-b-from-color":[{"mask-b-from":I()}],"mask-image-b-to-color":[{"mask-b-to":I()}],"mask-image-l-from-pos":[{"mask-l-from":ee()}],"mask-image-l-to-pos":[{"mask-l-to":ee()}],"mask-image-l-from-color":[{"mask-l-from":I()}],"mask-image-l-to-color":[{"mask-l-to":I()}],"mask-image-x-from-pos":[{"mask-x-from":ee()}],"mask-image-x-to-pos":[{"mask-x-to":ee()}],"mask-image-x-from-color":[{"mask-x-from":I()}],"mask-image-x-to-color":[{"mask-x-to":I()}],"mask-image-y-from-pos":[{"mask-y-from":ee()}],"mask-image-y-to-pos":[{"mask-y-to":ee()}],"mask-image-y-from-color":[{"mask-y-from":I()}],"mask-image-y-to-color":[{"mask-y-to":I()}],"mask-image-radial":[{"mask-radial":[Y,J]}],"mask-image-radial-from-pos":[{"mask-radial-from":ee()}],"mask-image-radial-to-pos":[{"mask-radial-to":ee()}],"mask-image-radial-from-color":[{"mask-radial-from":I()}],"mask-image-radial-to-color":[{"mask-radial-to":I()}],"mask-image-radial-shape":[{"mask-radial":[`circle`,`ellipse`]}],"mask-image-radial-size":[{"mask-radial":[{closest:[`side`,`corner`],farthest:[`side`,`corner`]}]}],"mask-image-radial-pos":[{"mask-radial-at":b()}],"mask-image-conic-pos":[{"mask-conic":[fn]}],"mask-image-conic-from-pos":[{"mask-conic-from":ee()}],"mask-image-conic-to-pos":[{"mask-conic-to":ee()}],"mask-image-conic-from-color":[{"mask-conic-from":I()}],"mask-image-conic-to-color":[{"mask-conic-to":I()}],"mask-mode":[{mask:[`alpha`,`luminance`,`match`]}],"mask-origin":[{"mask-origin":[`border`,`padding`,`content`,`fill`,`stroke`,`view`]}],"mask-position":[{mask:L()}],"mask-repeat":[{mask:R()}],"mask-size":[{mask:z()}],"mask-type":[{"mask-type":[`alpha`,`luminance`]}],"mask-image":[{mask:[`none`,Y,J]}],filter:[{filter:[``,`none`,Y,J]}],blur:[{blur:te()}],brightness:[{brightness:[fn,Y,J]}],contrast:[{contrast:[fn,Y,J]}],"drop-shadow":[{"drop-shadow":[``,`none`,p,In,An]}],"drop-shadow-color":[{"drop-shadow":I()}],grayscale:[{grayscale:[``,fn,Y,J]}],"hue-rotate":[{"hue-rotate":[fn,Y,J]}],invert:[{invert:[``,fn,Y,J]}],saturate:[{saturate:[fn,Y,J]}],sepia:[{sepia:[``,fn,Y,J]}],"backdrop-filter":[{"backdrop-filter":[``,`none`,Y,J]}],"backdrop-blur":[{"backdrop-blur":te()}],"backdrop-brightness":[{"backdrop-brightness":[fn,Y,J]}],"backdrop-contrast":[{"backdrop-contrast":[fn,Y,J]}],"backdrop-grayscale":[{"backdrop-grayscale":[``,fn,Y,J]}],"backdrop-hue-rotate":[{"backdrop-hue-rotate":[fn,Y,J]}],"backdrop-invert":[{"backdrop-invert":[``,fn,Y,J]}],"backdrop-opacity":[{"backdrop-opacity":[fn,Y,J]}],"backdrop-saturate":[{"backdrop-saturate":[fn,Y,J]}],"backdrop-sepia":[{"backdrop-sepia":[``,fn,Y,J]}],"border-collapse":[{border:[`collapse`,`separate`]}],"border-spacing":[{"border-spacing":w()}],"border-spacing-x":[{"border-spacing-x":w()}],"border-spacing-y":[{"border-spacing-y":w()}],"table-layout":[{table:[`auto`,`fixed`]}],caption:[{caption:[`top`,`bottom`]}],transition:[{transition:[``,`all`,`colors`,`opacity`,`shadow`,`transform`,`none`,Y,J]}],"transition-behavior":[{transition:[`normal`,`discrete`]}],duration:[{duration:[fn,`initial`,Y,J]}],ease:[{ease:[`linear`,`initial`,_,Y,J]}],delay:[{delay:[fn,Y,J]}],animate:[{animate:[`none`,v,Y,J]}],backface:[{backface:[`hidden`,`visible`]}],perspective:[{perspective:[h,Y,J]}],"perspective-origin":[{"perspective-origin":x()}],rotate:[{rotate:G()}],"rotate-x":[{"rotate-x":G()}],"rotate-y":[{"rotate-y":G()}],"rotate-z":[{"rotate-z":G()}],scale:[{scale:ne()}],"scale-x":[{"scale-x":ne()}],"scale-y":[{"scale-y":ne()}],"scale-z":[{"scale-z":ne()}],"scale-3d":[`scale-3d`],skew:[{skew:re()}],"skew-x":[{"skew-x":re()}],"skew-y":[{"skew-y":re()}],transform:[{transform:[Y,J,``,`none`,`gpu`,`cpu`]}],"transform-origin":[{origin:x()}],"transform-style":[{transform:[`3d`,`flat`]}],translate:[{translate:ie()}],"translate-x":[{"translate-x":ie()}],"translate-y":[{"translate-y":ie()}],"translate-z":[{"translate-z":ie()}],"translate-none":[`translate-none`],zoom:[{zoom:[pn,Y,J]}],accent:[{accent:I()}],appearance:[{appearance:[`none`,`auto`]}],"caret-color":[{caret:I()}],"color-scheme":[{scheme:[`normal`,`dark`,`light`,`light-dark`,`only-dark`,`only-light`]}],cursor:[{cursor:[`auto`,`default`,`pointer`,`wait`,`text`,`move`,`help`,`not-allowed`,`none`,`context-menu`,`progress`,`cell`,`crosshair`,`vertical-text`,`alias`,`copy`,`no-drop`,`grab`,`grabbing`,`all-scroll`,`col-resize`,`row-resize`,`n-resize`,`e-resize`,`s-resize`,`w-resize`,`ne-resize`,`nw-resize`,`se-resize`,`sw-resize`,`ew-resize`,`ns-resize`,`nesw-resize`,`nwse-resize`,`zoom-in`,`zoom-out`,Y,J]}],"field-sizing":[{"field-sizing":[`fixed`,`content`]}],"pointer-events":[{"pointer-events":[`auto`,`none`]}],resize:[{resize:[`none`,``,`y`,`x`]}],"scroll-behavior":[{scroll:[`auto`,`smooth`]}],"scrollbar-thumb-color":[{"scrollbar-thumb":I()}],"scrollbar-track-color":[{"scrollbar-track":I()}],"scrollbar-gutter":[{"scrollbar-gutter":[`auto`,`stable`,`both`]}],"scrollbar-w":[{scrollbar:[`auto`,`thin`,`none`]}],"scroll-m":[{"scroll-m":w()}],"scroll-mx":[{"scroll-mx":w()}],"scroll-my":[{"scroll-my":w()}],"scroll-ms":[{"scroll-ms":w()}],"scroll-me":[{"scroll-me":w()}],"scroll-mbs":[{"scroll-mbs":w()}],"scroll-mbe":[{"scroll-mbe":w()}],"scroll-mt":[{"scroll-mt":w()}],"scroll-mr":[{"scroll-mr":w()}],"scroll-mb":[{"scroll-mb":w()}],"scroll-ml":[{"scroll-ml":w()}],"scroll-p":[{"scroll-p":w()}],"scroll-px":[{"scroll-px":w()}],"scroll-py":[{"scroll-py":w()}],"scroll-ps":[{"scroll-ps":w()}],"scroll-pe":[{"scroll-pe":w()}],"scroll-pbs":[{"scroll-pbs":w()}],"scroll-pbe":[{"scroll-pbe":w()}],"scroll-pt":[{"scroll-pt":w()}],"scroll-pr":[{"scroll-pr":w()}],"scroll-pb":[{"scroll-pb":w()}],"scroll-pl":[{"scroll-pl":w()}],"snap-align":[{snap:[`start`,`end`,`center`,`align-none`]}],"snap-stop":[{snap:[`normal`,`always`]}],"snap-type":[{snap:[`none`,`x`,`y`,`both`]}],"snap-strictness":[{snap:[`mandatory`,`proximity`]}],touch:[{touch:[`auto`,`none`,`manipulation`]}],"touch-x":[{"touch-pan":[`x`,`left`,`right`]}],"touch-y":[{"touch-pan":[`y`,`up`,`down`]}],"touch-pz":[`touch-pinch-zoom`],select:[{select:[`none`,`text`,`all`,`auto`]}],"will-change":[{"will-change":[`auto`,`scroll`,`contents`,`transform`,Y,J]}],fill:[{fill:[`none`,...I()]}],"stroke-w":[{stroke:[fn,jn,wn,Tn]}],stroke:[{stroke:[`none`,...I()]}],"forced-color-adjust":[{"forced-color-adjust":[`auto`,`none`]}]},conflictingClassGroups:{"container-named":[`container-type`],overflow:[`overflow-x`,`overflow-y`],overscroll:[`overscroll-x`,`overscroll-y`],inset:[`inset-x`,`inset-y`,`inset-bs`,`inset-be`,`start`,`end`,`top`,`right`,`bottom`,`left`],"inset-x":[`right`,`left`],"inset-y":[`top`,`bottom`],flex:[`basis`,`grow`,`shrink`],gap:[`gap-x`,`gap-y`],p:[`px`,`py`,`ps`,`pe`,`pbs`,`pbe`,`pt`,`pr`,`pb`,`pl`],px:[`pr`,`pl`],py:[`pt`,`pb`],m:[`mx`,`my`,`ms`,`me`,`mbs`,`mbe`,`mt`,`mr`,`mb`,`ml`],mx:[`mr`,`ml`],my:[`mt`,`mb`],size:[`w`,`h`],"font-size":[`leading`],"fvn-normal":[`fvn-ordinal`,`fvn-slashed-zero`,`fvn-figure`,`fvn-spacing`,`fvn-fraction`],"fvn-ordinal":[`fvn-normal`],"fvn-slashed-zero":[`fvn-normal`],"fvn-figure":[`fvn-normal`],"fvn-spacing":[`fvn-normal`],"fvn-fraction":[`fvn-normal`],"line-clamp":[`display`,`overflow`],rounded:[`rounded-s`,`rounded-e`,`rounded-t`,`rounded-r`,`rounded-b`,`rounded-l`,`rounded-ss`,`rounded-se`,`rounded-ee`,`rounded-es`,`rounded-tl`,`rounded-tr`,`rounded-br`,`rounded-bl`],"rounded-s":[`rounded-ss`,`rounded-es`],"rounded-e":[`rounded-se`,`rounded-ee`],"rounded-t":[`rounded-tl`,`rounded-tr`],"rounded-r":[`rounded-tr`,`rounded-br`],"rounded-b":[`rounded-br`,`rounded-bl`],"rounded-l":[`rounded-tl`,`rounded-bl`],"border-spacing":[`border-spacing-x`,`border-spacing-y`],"border-w":[`border-w-x`,`border-w-y`,`border-w-s`,`border-w-e`,`border-w-bs`,`border-w-be`,`border-w-t`,`border-w-r`,`border-w-b`,`border-w-l`],"border-w-x":[`border-w-r`,`border-w-l`],"border-w-y":[`border-w-t`,`border-w-b`],"border-color":[`border-color-x`,`border-color-y`,`border-color-s`,`border-color-e`,`border-color-bs`,`border-color-be`,`border-color-t`,`border-color-r`,`border-color-b`,`border-color-l`],"border-color-x":[`border-color-r`,`border-color-l`],"border-color-y":[`border-color-t`,`border-color-b`],translate:[`translate-x`,`translate-y`,`translate-none`],"translate-none":[`translate`,`translate-x`,`translate-y`,`translate-z`],"scroll-m":[`scroll-mx`,`scroll-my`,`scroll-ms`,`scroll-me`,`scroll-mbs`,`scroll-mbe`,`scroll-mt`,`scroll-mr`,`scroll-mb`,`scroll-ml`],"scroll-mx":[`scroll-mr`,`scroll-ml`],"scroll-my":[`scroll-mt`,`scroll-mb`],"scroll-p":[`scroll-px`,`scroll-py`,`scroll-ps`,`scroll-pe`,`scroll-pbs`,`scroll-pbe`,`scroll-pt`,`scroll-pr`,`scroll-pb`,`scroll-pl`],"scroll-px":[`scroll-pr`,`scroll-pl`],"scroll-py":[`scroll-pt`,`scroll-pb`],touch:[`touch-x`,`touch-y`,`touch-pz`],"touch-x":[`touch`],"touch-y":[`touch`],"touch-pz":[`touch`]},conflictingClassGroupModifiers:{"font-size":[`leading`]},postfixLookupClassGroups:[`container-type`],orderSensitiveModifiers:[`*`,`**`,`after`,`backdrop`,`before`,`details-content`,`file`,`first-letter`,`first-line`,`marker`,`placeholder`,`selection`]}});function X(...e){return Jn(vt(e))}var Yn=o((e=>{var t=Symbol.for(`react.transitional.element`),n=Symbol.for(`react.fragment`);function r(e,n,r){var i=null;if(r!==void 0&&(i=``+r),n.key!==void 0&&(i=``+n.key),`key`in n)for(var a in r={},n)a!==`key`&&(r[a]=n[a]);else r=n;return n=r.ref,{$$typeof:t,type:e,key:i,ref:n===void 0?null:n,props:r}}e.Fragment=n,e.jsx=r,e.jsxs=r})),Xn=o(((e,t)=>{t.exports=Yn()})),Z=Xn();function Zn(e){return typeof e==`number`?`${e}px`:e}function Qn(e,t){let n=`min(${Zn(e)}, 64px)`;return typeof t==`number`&&t>0?`min(${n}, max(0px, calc(100% - ${t*2}px)))`:n}function $n({className:e,height:t=6,indicatorClassName:n,insetX:r,width:i=40}){let a={height:Zn(t),width:Qn(i,r)};return(0,Z.jsx)(`span`,{"aria-hidden":`true`,className:X(`relative shrink-0`,e),"data-inset-x":typeof r==`number`?String(r):void 0,"data-slot":`animated-loader`,style:a,children:(0,Z.jsx)(`span`,{className:X(`button-loader-indicator absolute inset-y-0 left-0 right-[65%] rounded-full bg-[color:var(--foreground)] opacity-90`,n),"data-slot":`animated-loader-indicator`})})}var er=4;function tr(e){return typeof e==`string`||typeof e==`number`?String(e):Array.isArray(e)?e.map(e=>tr(e)).join(``):_.isValidElement(e)?tr(e.props.children):``}function nr(e,t){if(typeof e==`function`){e(t);return}e&&typeof e==`object`&&(e.current=t)}function rr(e,t){let n={maxWidth:`${t}px`,minWidth:`${t}px`,width:`${t}px`};return typeof e==`function`?t=>({...e(t),...n}):{...e,...n}}function ir({ariaLabel:e,children:t,className:n,compactHeight:r=!1,disabled:i,iconOnly:a=!1,loading:o=!1,loadingHeight:s,loadingIndicatorClassName:c,loadingWidth:l,measurementKey:u,ref:d,style:f}){let p=_.useRef(null),m=_.useRef(null),h=a?4:16,g=s??(r?er:6),v=(e??tr(t).trim())||void 0,y=_.useCallback(e=>{p.current=e,nr(d,e)},[d]);return _.useLayoutEffect(()=>{if(o)return;let e=p.current;if(!e)return;let t=e.getBoundingClientRect().width;t>0&&(m.current=t)},[t,n,o,u,f]),{buttonAriaBusy:o||void 0,buttonAriaLabel:o?v:e,buttonClassName:o?`relative overflow-hidden transition-none !opacity-100`:void 0,buttonContent:o?(0,Z.jsx)(`span`,{"aria-hidden":`true`,className:`invisible inline-flex items-center`,"data-slot":`button-content`,style:{gap:`inherit`},children:t}):t,buttonDisabled:!!(i||o),buttonLoader:o?(0,Z.jsx)(`span`,{className:`pointer-events-none absolute inset-0 flex items-center justify-center`,"data-slot":`button-loader`,children:(0,Z.jsx)($n,{height:g,indicatorClassName:c,insetX:h,width:l??96})}):null,buttonRef:y,buttonStyle:o&&m.current?rr(f,m.current):f,dataLoading:o?`true`:void 0}}var ar=`aria-pressed:border-[color:color-mix(in_oklab,var(--border)_10%,transparent)] aria-pressed:bg-[color:color-mix(in_oklab,var(--link)_12%,transparent)] aria-pressed:text-[color:var(--foreground)] data-[pressed]:border-[color:color-mix(in_oklab,var(--border)_10%,transparent)] data-[pressed]:bg-[color:color-mix(in_oklab,var(--link)_12%,transparent)] data-[pressed]:text-[color:var(--foreground)]`,or=`aria-pressed:border-[color:color-mix(in_oklab,var(--border)_10%,transparent)] aria-pressed:bg-[color:color-mix(in_oklab,var(--link)_12%,transparent)] aria-pressed:text-[color:var(--foreground)] data-[pressed]:border-[color:color-mix(in_oklab,var(--border)_10%,transparent)] data-[pressed]:bg-[color:color-mix(in_oklab,var(--link)_12%,transparent)] data-[pressed]:text-[color:var(--foreground)] data-[state=on]:border-[color:color-mix(in_oklab,var(--border)_10%,transparent)] data-[state=on]:bg-[color:color-mix(in_oklab,var(--link)_12%,transparent)] data-[state=on]:text-[color:var(--foreground)]`,sr=`data-active:border-[color:color-mix(in_oklab,var(--border)_10%,transparent)] data-active:bg-[color:color-mix(in_oklab,var(--link)_12%,transparent)] data-active:text-[color:var(--foreground)]`;function cr(e){let t=e.hover.replaceAll(`hover:`,`focus:`);return[e.hover,t,e.active,e.persistent].join(` `)}function lr(e){switch(e){case`thin`:return`light`;case`light`:return`regular`;case`regular`:return`bold`;case`bold`:case`duotone`:case`fill`:return e;default:return`bold`}}function ur(e){if(typeof e==`string`)return e;let t=e;if(typeof t.displayName==`string`&&t.displayName.length>0)return t.displayName;if(typeof t.name==`string`&&t.name.length>0)return t.name;if(typeof t.render==`function`){let e=t.render;return e.displayName||e.name||null}return null}function dr(e){return ur(e.type)?.endsWith(`Icon`)??!1}function fr(e){return!1}function pr(e,t){return _.Children.map(e,e=>{if(!_.isValidElement(e))return e;let n=e.props.children===void 0?e.props.children:pr(e.props.children,t);if(!t)return n===e.props.children?e:_.cloneElement(e,void 0,n);if(dr(e)){let t=lr(e.props.weight);return n===e.props.children?_.cloneElement(e,{weight:t}):_.cloneElement(e,{weight:t},n)}return n===e.props.children?e:_.cloneElement(e,void 0,n)})}var mr=xt(`group/button inline-flex shrink-0 cursor-pointer items-center justify-center border border-transparent font-medium whitespace-nowrap transition-colors outline-none select-none focus-visible:border-[color:var(--ring)] focus-visible:ring-2 focus-visible:ring-[color:color-mix(in_oklab,var(--ring)_30%,transparent)] disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-[color:var(--destructive)] aria-invalid:ring-2 aria-invalid:ring-[color:color-mix(in_oklab,var(--destructive)_20%,transparent)] dark:aria-invalid:border-[color:color-mix(in_oklab,var(--destructive)_50%,transparent)] dark:aria-invalid:ring-[color:color-mix(in_oklab,var(--destructive)_40%,transparent)] [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4 [&_[data-icon]]:opacity-60 [&_[data-icon]]:transition-opacity hover:[&_[data-icon]]:opacity-100 data-[size=icon]:[&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-60 data-[size=icon]:[&_svg:not([data-slot='primitive-arrow-icon'])]:transition-opacity data-[size=icon]:hover:[&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-100 data-[size=icon-tight]:[&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-60 data-[size=icon-tight]:[&_svg:not([data-slot='primitive-arrow-icon'])]:transition-opacity data-[size=icon-tight]:hover:[&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-100 data-[size=icon-xxs]:[&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-60 data-[size=icon-xxs]:[&_svg:not([data-slot='primitive-arrow-icon'])]:transition-opacity data-[size=icon-xxs]:hover:[&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-100 data-[size=icon-xs]:[&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-60 data-[size=icon-xs]:[&_svg:not([data-slot='primitive-arrow-icon'])]:transition-opacity data-[size=icon-xs]:hover:[&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-100 data-[size=icon-sm]:[&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-60 data-[size=icon-sm]:[&_svg:not([data-slot='primitive-arrow-icon'])]:transition-opacity data-[size=icon-sm]:hover:[&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-100 data-[size=icon-lg]:[&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-60 data-[size=icon-lg]:[&_svg:not([data-slot='primitive-arrow-icon'])]:transition-opacity data-[size=icon-lg]:hover:[&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-100 data-[size=icon-xl]:[&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-60 data-[size=icon-xl]:[&_svg:not([data-slot='primitive-arrow-icon'])]:transition-opacity data-[size=icon-xl]:hover:[&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-100 data-[icon-active=true]:[&_[data-icon]]:!opacity-100 data-[icon-active=true]:[&_svg:not([data-slot='primitive-arrow-icon'])]:!opacity-100`,{variants:{motion:{default:``,static:``},radius:{default:`rounded-lg`,full:`rounded-full`,lg:`rounded-lg`,md:`rounded-md`,sm:`rounded-md`,"tab-control":`button-radius-tab-control`,xl:`rounded-xl`},variant:{default:`bg-[color:var(--primary)] text-[color:var(--primary-foreground)] ${cr({active:`active:bg-[color:color-mix(in_oklab,var(--primary)_82%,black)]`,hover:`hover:bg-[color:color-mix(in_oklab,var(--primary)_88%,black)]`,persistent:`aria-expanded:bg-[color:color-mix(in_oklab,var(--primary)_88%,black)] aria-pressed:bg-[color:color-mix(in_oklab,var(--primary)_82%,black)] data-open:bg-[color:color-mix(in_oklab,var(--primary)_88%,black)] data-popup-open:bg-[color:color-mix(in_oklab,var(--primary)_88%,black)] data-[state=open]:bg-[color:color-mix(in_oklab,var(--primary)_88%,black)] data-[pressed]:bg-[color:color-mix(in_oklab,var(--primary)_82%,black)]`})}`,outline:`border-[color:color-mix(in_oklab,var(--border)_12%,transparent)] bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] ${cr({active:`active:bg-[color:color-mix(in_oklab,var(--input)_15%,transparent)] active:text-[color:var(--foreground)]`,hover:`hover:!border-[color:color-mix(in_oklab,var(--border)_20%,transparent)] hover:bg-[color:color-mix(in_oklab,var(--input)_15%,transparent)] hover:text-[color:var(--foreground)]`,persistent:`aria-expanded:border-[color:color-mix(in_oklab,var(--border)_45%,transparent)] aria-expanded:bg-[color:color-mix(in_oklab,var(--input)_15%,transparent)] aria-expanded:text-[color:var(--foreground)] data-open:border-[color:color-mix(in_oklab,var(--border)_45%,transparent)] data-open:bg-[color:color-mix(in_oklab,var(--input)_15%,transparent)] data-open:text-[color:var(--foreground)] data-popup-open:border-[color:color-mix(in_oklab,var(--border)_45%,transparent)] data-popup-open:bg-[color:color-mix(in_oklab,var(--input)_15%,transparent)] data-popup-open:text-[color:var(--foreground)] data-[state=open]:border-[color:color-mix(in_oklab,var(--border)_45%,transparent)] data-[state=open]:bg-[color:color-mix(in_oklab,var(--input)_15%,transparent)] data-[state=open]:text-[color:var(--foreground)] ${ar}`})}`,"outline-inverted":`border-[color:color-mix(in_oklab,var(--background)_15%,transparent)] text-[color:color-mix(in_oklab,var(--background)_70%,transparent)] ${cr({active:`active:bg-[color:color-mix(in_oklab,var(--background)_10%,transparent)] active:text-[color:var(--background)]`,hover:`hover:bg-[color:color-mix(in_oklab,var(--background)_10%,transparent)] hover:text-[color:var(--background)]`,persistent:`aria-expanded:bg-[color:color-mix(in_oklab,var(--background)_10%,transparent)] aria-expanded:text-[color:var(--background)] aria-pressed:bg-[color:color-mix(in_oklab,var(--background)_10%,transparent)] aria-pressed:text-[color:var(--background)] data-open:bg-[color:color-mix(in_oklab,var(--background)_10%,transparent)] data-open:text-[color:var(--background)] data-popup-open:bg-[color:color-mix(in_oklab,var(--background)_10%,transparent)] data-popup-open:text-[color:var(--background)] data-[state=open]:bg-[color:color-mix(in_oklab,var(--background)_10%,transparent)] data-[state=open]:text-[color:var(--background)] data-[pressed]:bg-[color:color-mix(in_oklab,var(--background)_10%,transparent)] data-[pressed]:text-[color:var(--background)]`})}`,"destructive-outline":`border-[color:color-mix(in_oklab,var(--destructive)_80%,transparent)] bg-[color:color-mix(in_oklab,var(--destructive)_80%,transparent)] text-[color:var(--destructive-foreground)] ${cr({active:`active:bg-[color:color-mix(in_oklab,var(--destructive)_70%,transparent)]`,hover:`hover:border-[color:color-mix(in_oklab,var(--destructive)_70%,transparent)] hover:bg-[color:color-mix(in_oklab,var(--destructive)_70%,transparent)]`,persistent:`aria-expanded:bg-[color:color-mix(in_oklab,var(--destructive)_70%,transparent)] aria-pressed:bg-[color:color-mix(in_oklab,var(--destructive)_70%,transparent)] data-open:bg-[color:color-mix(in_oklab,var(--destructive)_70%,transparent)] data-popup-open:bg-[color:color-mix(in_oklab,var(--destructive)_70%,transparent)] data-[state=open]:bg-[color:color-mix(in_oklab,var(--destructive)_70%,transparent)] data-[pressed]:bg-[color:color-mix(in_oklab,var(--destructive)_70%,transparent)]`})} focus-visible:border-[color:var(--destructive)] focus-visible:ring-[color:color-mix(in_oklab,var(--destructive)_20%,transparent)] dark:focus-visible:ring-[color:color-mix(in_oklab,var(--destructive)_40%,transparent)]`,"destructive-outline-inverted":`border-[color:color-mix(in_oklab,var(--destructive)_80%,transparent)] bg-[color:color-mix(in_oklab,var(--destructive)_80%,transparent)] text-[color:var(--destructive-foreground)] ${cr({active:`active:bg-[color:color-mix(in_oklab,var(--destructive)_70%,transparent)]`,hover:`hover:border-[color:color-mix(in_oklab,var(--destructive)_70%,transparent)] hover:bg-[color:color-mix(in_oklab,var(--destructive)_70%,transparent)]`,persistent:`aria-expanded:bg-[color:color-mix(in_oklab,var(--destructive)_70%,transparent)] aria-pressed:bg-[color:color-mix(in_oklab,var(--destructive)_70%,transparent)] data-open:bg-[color:color-mix(in_oklab,var(--destructive)_70%,transparent)] data-popup-open:bg-[color:color-mix(in_oklab,var(--destructive)_70%,transparent)] data-[state=open]:bg-[color:color-mix(in_oklab,var(--destructive)_70%,transparent)] data-[pressed]:bg-[color:color-mix(in_oklab,var(--destructive)_70%,transparent)]`})} focus-visible:border-[color:var(--destructive)] focus-visible:ring-[color:color-mix(in_oklab,var(--destructive)_20%,transparent)]`,secondary:`bg-[color:color-mix(in_oklab,var(--secondary)_8%,transparent)] text-[color:var(--secondary-foreground)] ${cr({active:`active:bg-[color:color-mix(in_oklab,var(--secondary)_20%,transparent)]`,hover:`hover:bg-[color:color-mix(in_oklab,var(--secondary)_20%,transparent)]`,persistent:`aria-expanded:bg-[color:color-mix(in_oklab,var(--secondary)_20%,transparent)] aria-pressed:bg-[color:color-mix(in_oklab,var(--secondary)_20%,transparent)] data-open:bg-[color:color-mix(in_oklab,var(--secondary)_20%,transparent)] data-popup-open:bg-[color:color-mix(in_oklab,var(--secondary)_20%,transparent)] data-[state=open]:bg-[color:color-mix(in_oklab,var(--secondary)_20%,transparent)] data-[pressed]:bg-[color:color-mix(in_oklab,var(--secondary)_20%,transparent)]`})}`,"ghost-static":`bg-clip-border text-[color:var(--foreground)] ${cr({active:`active:bg-transparent active:text-[color:var(--foreground)]`,hover:`hover:bg-transparent hover:text-[color:var(--foreground)]`,persistent:`aria-expanded:bg-transparent aria-expanded:text-[color:var(--foreground)] aria-pressed:bg-transparent aria-pressed:text-[color:var(--foreground)] data-open:bg-transparent data-open:text-[color:var(--foreground)] data-popup-open:bg-transparent data-popup-open:text-[color:var(--foreground)] data-[state=open]:bg-transparent data-[state=open]:text-[color:var(--foreground)] data-[pressed]:bg-transparent data-[pressed]:text-[color:var(--foreground)]`})}`,send:`bg-[color:color-mix(in_oklab,var(--foreground)_80%,transparent)] !text-[color:color-mix(in_oklab,var(--background)_80%,transparent)] hover:!text-[color:color-mix(in_oklab,var(--background)_80%,transparent)] active:!text-[color:color-mix(in_oklab,var(--background)_80%,transparent)] [&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-100 hover:[&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-100 active:[&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-100 data-[size=icon]:[&_svg:not([data-slot='primitive-arrow-icon'])]:!opacity-100 data-[size=icon]:hover:[&_svg:not([data-slot='primitive-arrow-icon'])]:!opacity-100 data-[size=icon]:active:[&_svg:not([data-slot='primitive-arrow-icon'])]:!opacity-100 ${cr({active:`active:bg-[color:color-mix(in_oklab,var(--foreground)_80%,transparent)]`,hover:`hover:bg-[color:color-mix(in_oklab,var(--foreground)_80%,transparent)]`,persistent:`aria-expanded:bg-[color:color-mix(in_oklab,var(--foreground)_80%,transparent)] aria-pressed:bg-[color:color-mix(in_oklab,var(--foreground)_80%,transparent)] data-open:bg-[color:color-mix(in_oklab,var(--foreground)_80%,transparent)] data-popup-open:bg-[color:color-mix(in_oklab,var(--foreground)_80%,transparent)] data-[state=open]:bg-[color:color-mix(in_oklab,var(--foreground)_80%,transparent)] data-[pressed]:bg-[color:color-mix(in_oklab,var(--foreground)_80%,transparent)]`})}`,stop:`bg-[color:var(--foreground)] !text-[color:color-mix(in_oklab,var(--background)_90%,transparent)] hover:!text-[color:color-mix(in_oklab,var(--background)_90%,transparent)] active:!text-[color:color-mix(in_oklab,var(--background)_90%,transparent)] [&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-100 hover:[&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-100 active:[&_svg:not([data-slot='primitive-arrow-icon'])]:opacity-100 data-[size=icon]:[&_svg:not([data-slot='primitive-arrow-icon'])]:!opacity-100 data-[size=icon]:hover:[&_svg:not([data-slot='primitive-arrow-icon'])]:!opacity-100 data-[size=icon]:active:[&_svg:not([data-slot='primitive-arrow-icon'])]:!opacity-100 ${cr({active:`active:bg-[color:var(--foreground)]`,hover:`hover:bg-[color:var(--foreground)]`,persistent:`aria-expanded:bg-[color:var(--foreground)] aria-pressed:bg-[color:var(--foreground)] data-open:bg-[color:var(--foreground)] data-popup-open:bg-[color:var(--foreground)] data-[state=open]:bg-[color:var(--foreground)] data-[pressed]:bg-[color:var(--foreground)]`})}`,ghost:`bg-clip-border text-[color:var(--foreground)] ${cr({active:`active:bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] active:text-[color:var(--foreground)]`,hover:`hover:bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] hover:text-[color:var(--foreground)]`,persistent:`aria-expanded:bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] aria-expanded:text-[color:var(--foreground)] data-open:bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] data-open:text-[color:var(--foreground)] data-popup-open:bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] data-popup-open:text-[color:var(--foreground)] data-[state=open]:bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] data-[state=open]:text-[color:var(--foreground)] ${ar}`})}`,"ghost-muted":`bg-clip-border text-[color:color-mix(in_oklab,var(--foreground)_60%,transparent)] ${cr({active:`active:bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] active:text-[color:var(--foreground)]`,hover:`hover:bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] hover:text-[color:var(--foreground)]`,persistent:`aria-expanded:bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] aria-expanded:text-[color:var(--foreground)] data-open:bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] data-open:text-[color:var(--foreground)] data-popup-open:bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] data-popup-open:text-[color:var(--foreground)] data-[state=open]:bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] data-[state=open]:text-[color:var(--foreground)] ${ar}`})}`,destructive:`border-[color:color-mix(in_oklab,var(--destructive)_30%,transparent)] bg-[color:color-mix(in_oklab,var(--destructive)_15%,transparent)] text-[color:var(--destructive)] ${cr({active:`active:bg-[color:color-mix(in_oklab,var(--destructive)_25%,transparent)] active:text-[color:var(--destructive)]`,hover:`hover:border-[color:color-mix(in_oklab,var(--destructive)_60%,transparent)] hover:bg-[color:color-mix(in_oklab,var(--destructive)_25%,transparent)] hover:text-[color:var(--destructive)]`,persistent:`aria-expanded:bg-[color:color-mix(in_oklab,var(--destructive)_25%,transparent)] aria-expanded:text-[color:var(--destructive)] aria-pressed:bg-[color:color-mix(in_oklab,var(--destructive)_25%,transparent)] aria-pressed:text-[color:var(--destructive)] data-open:bg-[color:color-mix(in_oklab,var(--destructive)_25%,transparent)] data-open:text-[color:var(--destructive)] data-popup-open:bg-[color:color-mix(in_oklab,var(--destructive)_25%,transparent)] data-popup-open:text-[color:var(--destructive)] data-[state=open]:bg-[color:color-mix(in_oklab,var(--destructive)_25%,transparent)] data-[state=open]:text-[color:var(--destructive)] data-[pressed]:bg-[color:color-mix(in_oklab,var(--destructive)_25%,transparent)] data-[pressed]:text-[color:var(--destructive)]`})} focus-visible:border-[color:var(--destructive)] focus-visible:ring-[color:color-mix(in_oklab,var(--destructive)_20%,transparent)] dark:focus-visible:ring-[color:color-mix(in_oklab,var(--destructive)_40%,transparent)]`,"link-solid":`bg-[color:var(--link)] text-[color:var(--background)] ${cr({active:`active:bg-[color:color-mix(in_oklab,var(--link)_82%,black)]`,hover:`hover:bg-[color:color-mix(in_oklab,var(--link)_88%,black)]`,persistent:`aria-expanded:bg-[color:color-mix(in_oklab,var(--link)_88%,black)] aria-pressed:bg-[color:color-mix(in_oklab,var(--link)_82%,black)] data-open:bg-[color:color-mix(in_oklab,var(--link)_88%,black)] data-popup-open:bg-[color:color-mix(in_oklab,var(--link)_88%,black)] data-[state=open]:bg-[color:color-mix(in_oklab,var(--link)_88%,black)] data-[pressed]:bg-[color:color-mix(in_oklab,var(--link)_82%,black)]`})}`,link:`text-[color:var(--primary)] underline-offset-4 ${cr({active:`active:underline`,hover:`hover:underline`,persistent:`aria-expanded:underline aria-pressed:underline data-open:underline data-popup-open:underline data-[state=open]:underline data-[pressed]:underline`})}`,"toolbar-ghost":``,"toolbar-secondary":``},size:{default:`h-7 gap-1 px-2 text-[13px] leading-[1.125rem] has-data-[icon=inline-end]:pr-1.5 has-data-[icon=inline-start]:pl-1.5 [&_svg:not([class*='size-'])]:size-3.5`,xxs:`h-[18px] gap-1 px-1.5 text-[11px] has-data-[icon=inline-end]:pr-1 has-data-[icon=inline-start]:pl-1 [&_svg:not([class*='size-'])]:size-2.5`,xs:`h-[22px] gap-1 px-2 text-[12px] has-data-[icon=inline-end]:pr-1.5 has-data-[icon=inline-start]:pl-1.5 [&_svg:not([class*='size-'])]:size-2.5`,sm:`h-6 gap-1 px-2 text-xs/relaxed has-data-[icon=inline-end]:pr-1.5 has-data-[icon=inline-start]:pl-1.5 [&_svg:not([class*='size-'])]:size-3`,lg:`h-[34px] gap-1 px-3.5 text-sm/relaxed tracking-tight has-data-[icon=inline-end]:pr-3 has-data-[icon=inline-start]:pl-3 [&_svg:not([class*='size-'])]:size-3.5`,xl:`button-xl-icon-size h-10 gap-1.5 px-3 text-sm/relaxed has-data-[icon=inline-end]:pr-2.5 has-data-[icon=inline-start]:pl-2.5`,icon:`size-7 text-[13px] leading-[1.125rem] [&_svg:not([class*='size-'])]:size-3.5`,"icon-tight":`h-7 px-1.5 text-[13px] leading-[1.125rem] [&_svg:not([class*='size-'])]:size-3.5`,"icon-xxs":`size-[18px] text-[11px] [&_svg:not([class*='size-'])]:size-2.5`,"icon-xs":`size-[22px] text-[12px] [&_svg:not([class*='size-'])]:size-2.5`,"icon-sm":`size-6 text-xs/relaxed [&_svg:not([class*='size-'])]:size-3`,"icon-lg":`size-[34px] text-sm/relaxed tracking-tight [&_svg:not([class*='size-'])]:size-4`,"icon-xl":`button-xl-icon-size size-10 text-sm/relaxed`}},defaultVariants:{motion:`default`,radius:`default`,variant:`default`,size:`default`}});function hr(e){return e===`xxs`||e===`xs`||e===`sm`||e===`icon-xxs`||e===`icon-xs`||e===`icon-sm`}function gr({"aria-label":e,"data-slot":t,children:n,className:r,disabled:i,loading:a=!1,loadingHeight:o,loadingIndicatorClassName:s,loadingWidth:c,motion:l=`default`,radius:u=`default`,ref:d,size:f=`default`,style:p,variant:m=`default`,...h}){let g=u==="default"&&(f===`xxs`||f===`icon-xxs`)?`sm`:u,{buttonAriaBusy:_,buttonAriaLabel:v,buttonClassName:y,buttonContent:b,buttonDisabled:x,buttonLoader:S,buttonRef:C,buttonStyle:w,dataLoading:T}=ir({ariaLabel:e,children:pr(n,fr(f)),className:r,compactHeight:hr(f),disabled:i,iconOnly:typeof f==`string`&&f.startsWith(`icon`),loading:a,loadingHeight:o,loadingIndicatorClassName:s??(m==="default"?`bg-[color:var(--primary-foreground)]`:m===`link-solid`?`bg-[color:var(--background)]`:void 0),loadingWidth:c,measurementKey:[l,g,f,m].join(`:`),ref:d,style:p});return(0,Z.jsxs)(ht,{...h,"aria-label":v,"aria-busy":_,"data-slot":t??`button`,"data-loading":T,"data-radius":g??void 0,"data-size":f??void 0,"data-variant":m??void 0,disabled:x,ref:C,className:X(mr({motion:l,radius:g,variant:m,size:f}),r,y),style:w,children:[b,S]})}var _r={badInput:!1,customError:!1,patternMismatch:!1,rangeOverflow:!1,rangeUnderflow:!1,stepMismatch:!1,tooLong:!1,tooShort:!1,typeMismatch:!1,valid:null,valueMissing:!1},vr={disabled:!1,valid:null,touched:!1,dirty:!1,filled:!1,focused:!1},yr={valid(e){return e===null?null:e?{"data-valid":``}:{"data-invalid":``}}},br={invalid:void 0,name:void 0,validityData:{state:_r,errors:[],error:``,value:``,initialValue:null},setValidityData:rt,disabled:void 0,setTouched:rt,setDirty:rt,setFilled:rt,setFocused:rt,validationMode:`onSubmit`,shouldValidateOnChange:()=>!1,state:vr,registerFieldControl:rt,validation:{getValidationProps:(e,t=at)=>t,inputRef:{current:null},registeredInputs:new Map,registerInput:rt,getInputControl:()=>null,commit:async()=>{},change:rt}},xr=_.createContext(br);function Sr(e=!0){let t=_.useContext(xr);if(t.setValidityData===rt&&!e)throw Error(ze(28));return t}var Cr=_.createContext({elementRef:{current:null},formRef:{current:{fields:new Map}},errors:{},clearErrors:rt,validationMode:`onSubmit`,submitAttemptedRef:{current:!1}});function wr(){return _.useContext(Cr)}var Tr=0;function Er(e,t=`mui`){let[n,r]=_.useState(e),i=e||n;return _.useEffect(()=>{n??(Tr+=1,r(`${t}-${Tr}`))},[n,t]),i}var Dr=he.useId;function Or(e,t){if(Dr!==void 0){let n=Dr();return e??(t?`${t}-${n}`:n)}return Er(e,t)}function kr(e){return Or(e,`base-ui`)}var Ar=_.createContext({controlId:void 0,registerControlId:rt,labelId:void 0,setLabelId:rt,messageIds:[],setMessageIds:rt,getDescriptionProps:e=>e});function jr(){return _.useContext(Ar)}function Mr(e,t,n,r=!0,i){let[a,o]=_.useState(),s=kr(i?`${i}-label`:void 0),c=e??t??a;return q(()=>{let i=e||t||!r?void 0:Nr(n.current,s);a!==i&&o(i)}),c}function Nr(e,t){let n=Pr(e);if(n)return!n.id&&t&&(n.id=t),n.id||void 0}function Pr(e){if(!e)return;let t=e.parentElement;if(t&&t.tagName===`LABEL`)return t;let n=e.id;if(n){let t=e.nextElementSibling;if(t&&t.htmlFor===n)return t}let r=e.labels;return r&&r[0]}function Fr(e={}){let{id:t,implicit:n=!1,controlRef:r}=e,{controlId:i,registerControlId:a}=jr(),o=kr(t),s=n?i:void 0,c=_e(()=>Symbol()),l=_.useRef(!1),u=_.useRef(t!=null),d=K(()=>{!l.current||a===rt||(l.current=!1,a(c.current,void 0))});return q(()=>{if(a===rt)return;let e;if(n){let n=r?.current;e=V(n)&&n.closest(`label`)!=null?t??null:s??o}else if(t!=null)u.current=!0,e=t;else if(u.current)e=o;else{d();return}if(e===void 0){d();return}l.current=!0,a(c.current,e)},[t,r,s,a,n,o,c,d]),_.useEffect(()=>d,[d]),i??o}function Ir(){return typeof navigator>`u`?{userAgent:``,platform:``,maxTouchPoints:0}:{userAgent:navigator.userAgent,platform:navigator.platform??``,maxTouchPoints:navigator.maxTouchPoints??0}}var{userAgent:Lr,platform:Rr,maxTouchPoints:zr}=Ir(),Br=Lr.toLowerCase(),Vr=Rr.toLowerCase(),Hr=/^i(os$|p)/.test(Vr)||Vr===`macintel`&&zr>1,Ur=`android`,Wr=Vr===Ur||Br.includes(Ur),Gr=!Hr&&Vr.startsWith(`mac`);Vr.startsWith(`win`),!Wr&&/^(linux|chrome os)/.test(Vr);var Kr=Gr||Hr,qr=typeof CSS<`u`&&!!CSS.supports?.(`-webkit-backdrop-filter:none`);!qr&&Br.includes(`firefox`),!qr&&Br.includes(`chrom`);var Jr=Kr,Yr=/jsdom|happydom/.test(Br),Xr=`data-base-ui-focusable`,Zr=`input:not([type='hidden']):not([disabled]),[contenteditable]:not([contenteditable='false']),textarea:not([disabled])`,Qr=`ArrowLeft`,$r=`ArrowRight`,ei=`ArrowUp`,ti=`ArrowDown`;function ni(e){let t=e.activeElement;for(;t?.shadowRoot?.activeElement!=null;)t=t.shadowRoot.activeElement;return t}function Q(e,t){if(!e||!t)return!1;let n=t.getRootNode?.();if(e.contains(t))return!0;if(n&&U(n)){let n=t;for(;n;){if(e===n)return!0;n=n.parentNode||n.host}}return!1}function ri(e){return`composedPath`in e?e.composedPath()[0]:e.target}function ii(e,t){if(!V(e))return!1;let n=e;if(t.hasElement(n))return!n.hasAttribute(`data-trigger-disabled`);for(let[,e]of t.entries())if(Q(e,n))return!e.hasAttribute(`data-trigger-disabled`);return!1}function ai(e,t){if(t==null)return!1;if(`composedPath`in e)return e.composedPath().includes(t);let n=e;return n.target!=null&&t.contains(n.target)}function oi(e){return e.matches(`html,body`)}function si(e){return H(e)&&e.matches(`input:not([type='hidden']):not([disabled]),[contenteditable]:not([contenteditable='false']),textarea:not([disabled])`)}function ci(e){return e?.closest(`button,a[href],[role="button"],select,[tabindex]:not([tabindex="-1"]),${Zr}`)!=null}function li(e){return e?e.getAttribute(`role`)===`combobox`&&si(e):!1}function ui(e){if(!e||Yr)return!0;try{return e.matches(`:focus-visible`)}catch{return!0}}function di(e){return e?e.hasAttribute(`data-base-ui-focusable`)?e:e.querySelector(`[data-base-ui-focusable]`)||e:null}function fi(e,t,n=!0){return e.filter(e=>e.parentId===t).flatMap(t=>[...!n||t.context?.open?[t]:[],...fi(e,t.id,n)])}function pi(e,t){let n=[],r=e.find(e=>e.id===t)?.parentId;for(;r;){let t=e.find(e=>e.id===r);r=t?.parentId,t&&(n=n.concat(t))}return n}function mi(e){e.preventDefault(),e.stopPropagation()}function hi(e){return`nativeEvent`in e}function gi(e){return e.pointerType===``&&e.isTrusted?!0:Wr&&e.pointerType?e.type===`click`&&e.buttons===1:e.detail===0&&!e.pointerType}function _i(e){return Yr?!1:!Wr&&e.width===0&&e.height===0||Wr&&e.width===1&&e.height===1&&e.pressure===0&&e.detail===0&&e.pointerType===`mouse`||e.width<1&&e.height<1&&e.pressure===0&&e.detail===0&&e.pointerType===`touch`}function vi(e,t){let n=[`mouse`,`pen`];return t||n.push(``,void 0),n.includes(e)}function yi(e){let t=e.type;return t===`click`||t===`mousedown`||t===`keydown`||t===`keyup`}var bi=Math.min,xi=Math.max,Si=Math.round,Ci=Math.floor,wi=e=>({x:e,y:e}),Ti={left:`right`,right:`left`,bottom:`top`,top:`bottom`};function Ei(e,t,n){return xi(e,bi(t,n))}function Di(e,t){return typeof e==`function`?e(t):e}function Oi(e){return e.split(`-`)[0]}function ki(e){return e.split(`-`)[1]}function Ai(e){return e===`x`?`y`:`x`}function ji(e){return e===`y`?`height`:`width`}function Mi(e){let t=e[0];return t===`t`||t===`b`?`y`:`x`}function Ni(e){return Ai(Mi(e))}function Pi(e,t,n){n===void 0&&(n=!1);let r=ki(e),i=Ni(e),a=ji(i),o=i===`x`?r===(n?`end`:`start`)?`right`:`left`:r===`start`?`bottom`:`top`;return t.reference[a]>t.floating[a]&&(o=Ui(o)),[o,Ui(o)]}function Fi(e){let t=Ui(e);return[Ii(e),t,Ii(t)]}function Ii(e){return e.includes(`start`)?e.replace(`start`,`end`):e.replace(`end`,`start`)}var Li=[`left`,`right`],Ri=[`right`,`left`],zi=[`top`,`bottom`],Bi=[`bottom`,`top`];function Vi(e,t,n){switch(e){case`top`:case`bottom`:return n?t?Ri:Li:t?Li:Ri;case`left`:case`right`:return t?zi:Bi;default:return[]}}function Hi(e,t,n,r){let i=ki(e),a=Vi(Oi(e),n===`start`,r);return i&&(a=a.map(e=>e+`-`+i),t&&(a=a.concat(a.map(Ii)))),a}function Ui(e){let t=Oi(e);return Ti[t]+e.slice(t.length)}function Wi(e){return{top:e.top??0,right:e.right??0,bottom:e.bottom??0,left:e.left??0}}function Gi(e){return typeof e==`number`?{top:e,right:e,bottom:e,left:e}:Wi(e)}function Ki(e){let{x:t,y:n,width:r,height:i}=e;return{width:r,height:i,top:n,left:t,right:t+r,bottom:n+i,x:t,y:n}}function qi(e,t){return t<0||t>=e.length}function Ji(e,t){return Xi(e.current,{disabledIndices:t})}function Yi(e,t){return Xi(e.current,{decrement:!0,startingIndex:e.current.length,disabledIndices:t})}function Xi(e,{startingIndex:t=-1,decrement:n=!1,disabledIndices:r,amount:i=1}={}){let a=t;do a+=n?-i:i;while(a>=0&&a<=e.length-1&&Zi(e,a,r));return a}function Zi(e,t,n){if(typeof n==`function`?n(t):n?.includes(t)??!1)return!0;let r=e[t];return r?!$i(r)||r.matches(`:disabled`)?!0:!n&&(r.hasAttribute(`disabled`)||r.getAttribute(`aria-disabled`)===`true`):!1}function Qi(e){return e.visibility===`hidden`||e.visibility===`collapse`}function $i(e,t=e?le(e):null){return!e||!e.isConnected||!t||Qi(t)?!1:typeof e.checkVisibility==`function`?e.checkVisibility():t.display!==`none`&&t.display!==`contents`}var ea=`a[href],button,input,select,textarea,summary,details,iframe,object,embed,[tabindex],[contenteditable]:not([contenteditable="false"]),audio[controls],video[controls]`;function ta(e){let t=e.assignedSlot;if(t)return t;if(e.parentElement)return e.parentElement;let n=e.getRootNode();return U(n)?n.host:null}function na(e){for(let t of Array.from(e.children))if(L(t)===`summary`)return t;return null}function ra(e,t){let n=na(t);return!!n&&(e===n||Q(n,e))}function ia(e){let t=e?L(e):``;return e!=null&&e.matches(ea)&&(t!==`summary`||e.parentElement!=null&&L(e.parentElement)===`details`&&na(e.parentElement)===e)&&(t!==`details`||na(e)==null)&&(t!==`input`||e.type!==`hidden`)}function aa(e){if(!ia(e)||!e.isConnected||e.matches(`:disabled`))return!1;for(let t=e;t;t=ta(t)){let n=t!==e,r=L(t)===`slot`;if(t.hasAttribute(`inert`)||n&&L(t)===`details`&&!t.open&&!ra(e,t)||t.hasAttribute(`hidden`)||!r&&!oa(t,n))return!1}return!0}function oa(e,t){let n=le(e);return t?n.display!==`none`:$i(e,n)}function sa(e){let t=e.tabIndex;if(t<0){let t=L(e);if(t===`details`||t===`audio`||t===`video`||H(e)&&e.isContentEditable)return 0}return t}function ca(e){if(L(e)!==`input`)return null;let t=e;return t.type===`radio`&&t.name!==``?t:null}function la(e,t){let n=ca(e);if(!n)return!0;let r=t.find(e=>{let t=ca(e);return t?.name===n.name&&t.form===n.form&&t.checked});return r?r===n:t.find(e=>{let t=ca(e);return t?.name===n.name&&t.form===n.form})===n}function ua(e){if(H(e)&&L(e)===`slot`){let t=e.assignedElements({flatten:!0});if(t.length>0)return t}return H(e)&&e.shadowRoot?Array.from(e.shadowRoot.children):Array.from(e.children)}function da(e,t){ua(e).forEach(e=>{ia(e)&&t.push(e),da(e,t)})}function fa(e,t,n){ua(e).forEach(e=>{H(e)&&e.matches(t)&&n.push(e),fa(e,t,n)})}function pa(e){return aa(e)&&sa(e)>=0}function ma(e){let t=[];return da(e,t),t.filter(aa)}function ha(e){let t=ma(e);return t.filter(e=>sa(e)>=0&&la(e,t))}function ga(e,t){let n=ha(e),r=n.length;if(r===0)return;let i=ni(Ue(e)),a=n.indexOf(i);return n[a===-1?t===1?0:r-1:a+t]}function _a(e){return ga(Ue(e).body,1)||e}function va(e){return ga(Ue(e).body,-1)||e}function ya(e,t){if(!e)return null;let n=ha(Ue(e).body),r=n.length;if(r===0)return null;let i=n.indexOf(e);return i===-1?null:n[(i+t+r)%r]}function ba(e){return ya(e,1)}function xa(e){return ya(e,-1)}function Sa(e,t){let n=t||e.currentTarget,r=e.relatedTarget;return!r||!Q(n,r)}function Ca(e){ha(e).forEach(e=>{e.dataset.tabindex=e.getAttribute(`tabindex`)||``,e.setAttribute(`tabindex`,`-1`)})}function wa(e){let t=[];fa(e,`[data-tabindex]`,t),t.forEach(e=>{let t=e.dataset.tabindex;delete e.dataset.tabindex,t?e.setAttribute(`tabindex`,t):e.removeAttribute(`tabindex`)})}function Ta(e){_.useEffect(e,it)}var Ea=0,Da=class e{static create(){return new e}currentId=Ea;start(e,t){this.clear(),this.currentId=setTimeout(()=>{this.currentId=Ea,t()},e)}isStarted(){return this.currentId!==Ea}clear=()=>{this.currentId!==Ea&&(clearTimeout(this.currentId),this.currentId=Ea)};disposeEffect=()=>this.clear};function Oa(){let e=_e(Da.create).current;return Ta(e.disposeEffect),e}var ka=null;globalThis.requestAnimationFrame;var Aa=new class{callbacks=[];callbacksCount=0;nextId=1;startId=1;isScheduled=!1;tick=e=>{this.isScheduled=!1;let t=this.callbacks,n=this.callbacksCount;if(this.callbacks=[],this.callbacksCount=0,this.startId=this.nextId,n>0)for(let n=0;n<t.length;n+=1)t[n]?.(e)};request(e){let t=this.nextId;return this.nextId+=1,this.callbacks.push(e),this.callbacksCount+=1,this.isScheduled||=(requestAnimationFrame(this.tick),!0),t}cancel(e){let t=e-this.startId;t<0||t>=this.callbacks.length||(this.callbacks[t]=null,--this.callbacksCount)}},ja=class e{static create(){return new e}static request(e){return Aa.request(e)}static cancel(e){return Aa.cancel(e)}currentId=ka;request(e){this.cancel(),this.currentId=Aa.request(()=>{this.currentId=ka,e()})}cancel=()=>{this.currentId!==ka&&(Aa.cancel(this.currentId),this.currentId=ka)};disposeEffect=()=>this.cancel};function Ma(){let e=_e(ja.create).current;return Ta(e.disposeEffect),e}function Na(e){return e==null?e:`current`in e?e.current:e}var Pa=c(m(),1);function Fa(e,t=!1){let n=Ma();return K((r,i=null)=>{n.cancel();let a=Na(e);if(a==null)return;let o=a,s=()=>{Pa.flushSync(r)};if(typeof o.getAnimations!=`function`||globalThis.BASE_UI_ANIMATIONS_DISABLED){r();return}function c(){Promise.all(o.getAnimations().map(e=>e.finished)).then(()=>{i?.aborted||s()},()=>{if(!i?.aborted){if(o.getAnimations().some(e=>e.pending||e.playState!==`finished`)){c();return}s()}})}if(t){let e=`data-starting-style`;if(!o.hasAttribute(e)){n.request(c);return}let t=new MutationObserver(()=>{o.hasAttribute(e)||(t.disconnect(),c())});t.observe(o,{attributes:!0,attributeFilter:[e]}),i?.addEventListener(`abort`,()=>t.disconnect(),{once:!0});return}n.request(c)})}function Ia(e){let{enabled:t=!0,open:n,ref:r,onComplete:i}=e,a=K(i),o=Fa(r,n);_.useEffect(()=>{if(!t)return;let e=new AbortController;return o(a,e.signal),()=>{e.abort()}},[t,n,a,o])}var La=function(e){return e.startingStyle=`data-starting-style`,e.endingStyle=`data-ending-style`,e}({}),Ra={"data-starting-style":``},za={"data-ending-style":``},Ba={transitionStatus(e){return e===`starting`?Ra:e===`ending`?za:null}};function Va(e,t=!1,n=!1){let[r,i]=_.useState(e&&t?`idle`:void 0),[a,o]=_.useState(e);return e&&!a&&(o(!0),i(`starting`)),!e&&a&&r!==`ending`&&!n&&i(`ending`),!e&&!a&&r===`ending`&&i(void 0),q(()=>{if(!e&&a&&r!==`ending`&&n){let e=ja.request(()=>{i(`ending`)});return()=>{ja.cancel(e)}}},[e,a,r,n]),q(()=>{if(!e||t)return;let n=ja.request(()=>{i(void 0)});return()=>{ja.cancel(n)}},[t,e]),q(()=>{if(!e||!t)return;e&&a&&r!==`idle`&&i(`starting`);let n=ja.request(()=>{i(`idle`)});return()=>{ja.cancel(n)}},[t,e,a,r]),{mounted:a,setMounted:o,transitionStatus:r}}function Ha({controlled:e,default:t,name:n,state:r=`value`}){let{current:i}=_.useRef(e!==void 0),[a,o]=_.useState(t);return[i?e:a,_.useCallback(e=>{i||o(e)},[])]}function Ua(e,t,n,r,i=!0,a){let{registerFieldControl:o}=Sr(),s=_e(()=>Symbol());q(()=>{let c=s.current;if(!i){o(c,void 0);return}o(c,{controlRef:e,getValue:r,id:t,name:a,value:n})},[e,i,r,t,a,o,s,n]),q(()=>{let e=s.current;return()=>{o(e,void 0)}},[o,s])}var Wa=`none`,Ga=`trigger-press`,Ka=`trigger-hover`,qa=`trigger-focus`,Ja=`outside-press`,Ya=`item-press`,Xa=`close-press`,Za=`track-press`,Qa=`input-change`,$a=`focus-out`,eo=`escape-key`,to=`list-navigation`,no=`keyboard`,ro=`drag`,io=`cancel-open`,ao=`disabled`,oo=`missing`,so=`initial`,co=`imperative-action`,lo=`window-resize`;function $(e,t,n,r){let i=!1,a=!1,o=r??at;return{reason:e,event:t??new Event(`base-ui`),cancel(){i=!0},allowPropagation(){a=!0},get isCanceled(){return i},get isPropagationAllowed(){return a},trigger:n,...o}}function uo(e,t,n){let r=n??at;return{reason:e,event:t??new Event(`base-ui`),...r}}var fo=_.forwardRef(function(e,t){let{render:n,className:r,id:i,name:a,value:o,disabled:s=!1,onValueChange:c,defaultValue:l,autoFocus:u=!1,style:d,...f}=e,{state:p,name:m,disabled:h,setTouched:g,setDirty:v,validityData:y,setFocused:b,setFilled:x,validationMode:S,validation:C}=Sr(),{clearErrors:w}=wr(),T=h||s,E=m??a,D={...p,disabled:T},{labelId:O}=jr(),k=Fr({id:i});q(()=>{let e=o!=null;C.inputRef.current?.value||e&&o!==``?x(!0):e&&o===``&&x(!1)},[C.inputRef,x,o]);let A=_.useRef(null);q(()=>{u&&A.current===ni(Ue(A.current))&&b(!0)},[u,b]);let[j]=Ha({controlled:o,default:l,name:`FieldControl`,state:`value`}),M=o!==void 0,N=M?j:void 0,P=K(()=>C.inputRef.current?.value);return Ua(C.inputRef,k,N,P,!T,a),lt(`input`,e,{ref:[t,A],state:D,props:[{id:k,disabled:T,name:E,ref:C.inputRef,"aria-labelledby":O,autoFocus:u,...M?{value:N}:{defaultValue:l},onChange(e){let t=e.currentTarget.value;c?.(t,$(Wa,e.nativeEvent)),v(t!==(y.initialValue??``)),x(t!==``),e.nativeEvent.defaultPrevented||(w(E),C.change(t))},onFocus(){b(!0)},onBlur(e){g(!0),b(!1),S===`onBlur`&&C.commit(e.currentTarget.value)},onKeyDown(e){e.currentTarget.tagName===`INPUT`&&e.key===`Enter`&&(g(!0),C.commit(e.currentTarget.value))}},f,e=>C.getValidationProps(T,e)],stateAttributesMapping:yr})}),po=_.forwardRef(function(e,t){return(0,Z.jsx)(fo,{ref:t,...e})}),mo=`border-[color:color-mix(in_oklab,var(--border)_12%,transparent)] bg-[color:color-mix(in_oklab,var(--input)_5%,transparent)] bg-clip-padding text-[color:var(--foreground)]`,ho=[`w-full min-w-0 cursor-text rounded-lg border transition-colors outline-none`,`file:inline-flex file:border-0 file:bg-transparent file:font-medium file:text-[color:var(--foreground)]`,`placeholder:text-[color:var(--muted-foreground)]`,`[&:not(:focus):hover]:!border-[color:color-mix(in_oklab,var(--border)_20%,transparent)] [&:not(:focus):hover]:text-[color:var(--foreground)]`,`focus:border-[color:color-mix(in_oklab,var(--border)_30%,transparent)]`,`focus-visible:border-[color:color-mix(in_oklab,var(--border)_30%,transparent)]`,`disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50`,`aria-invalid:border-[color:var(--destructive)]`,`dark:aria-invalid:border-[color:color-mix(in_oklab,var(--destructive)_50%,transparent)]`,mo].join(` `),go=xt(ho,{variants:{size:{default:`h-7 px-2 py-0.5 text-xs/relaxed file:h-6 file:text-xs/relaxed`,lg:`h-8 px-2.5 py-1 text-sm/relaxed file:h-7 file:text-sm/relaxed`,sm:`h-6 px-2 py-0 text-xs/relaxed file:h-5 file:text-xs/relaxed`,xl:`h-10 px-3 py-1.5 text-base/relaxed file:h-9 file:text-base/relaxed`}},defaultVariants:{size:`default`}});function _o(e){try{let t=e.selectionEnd??e.value.length;e.setSelectionRange(t,t)}catch{}}function vo({className:e,collapseSelectionOnBlur:t=!1,onBlur:n,size:r,type:i,...a}){return(0,Z.jsx)(po,{type:i,"data-slot":`input`,className:X(go({size:r}),e),onBlur:e=>{t&&_o(e.currentTarget),n?.(e)},...a})}var yo=[],bo=void 0;function xo(){return bo}function So(e){yo.push(e)}function Co(e){let t=(t,n)=>{let r=_e(To).current,i;try{bo=r;for(let e of yo)e.before(r);i=e(t,n);for(let e of yo)e.after(r);r.didInitialize=!0}finally{bo=void 0}return i};return t.displayName=e.displayName||e.name,t}function wo(e){return _.forwardRef(Co(e))}function To(){return{didInitialize:!1}}var Eo=_.createContext(void 0);function Do(e){let t=_.useContext(Eo);if(t===void 0&&!e)throw Error(ze(72));return t}function Oo(e,t){return t!=null&&!vi(t)?0:typeof e==`function`?e():e}function ko(e,t,n){let r=Oo(e,n);return typeof r==`number`?r:r?.[t]}function Ao(e){return typeof e==`function`?e():e}function jo(e,t){return t||e===`click`||e===`mousedown`}function Mo(e){return e?.includes(`mouse`)&&e!==`mousedown`}var No=_.createContext({hasProvider:!1,timeoutMs:0,delayRef:{current:0},initialDelayRef:{current:0},timeout:new Da,currentIdRef:{current:null},currentContextRef:{current:null}});function Po(e,t){e.current=t.current}function Fo(e){let{children:t,delay:n,timeoutMs:r=0}=e,i=_.useRef(n),a=_.useRef(n),o=_.useRef(null),s=_.useRef(null),c=Oa();return q(()=>{if(a.current=n,!o.current){i.current=n;return}i.current={open:ko(i.current,`open`),close:ko(n,`close`)}},[n,o,i,a]),(0,Z.jsx)(No.Provider,{value:_.useMemo(()=>({hasProvider:!0,delayRef:i,initialDelayRef:a,currentIdRef:o,timeoutMs:r,currentContextRef:s,timeout:c}),[r,c]),children:t})}function Io(e,t={open:!1}){let{open:n}=t,r=`rootStore`in e?e.rootStore:e,i=r.useState(`floatingId`),{currentIdRef:a,delayRef:o,timeoutMs:s,initialDelayRef:c,currentContextRef:l,hasProvider:u,timeout:d}=_.useContext(No),[f,p]=_.useState(!1),m=_.useRef(n);return q(()=>{m.current=n},[n]),q(()=>{function e(){l.current?.setIsInstantPhase(!1),a.current=null,l.current=null,o.current=c.current,d.clear()}if(a.current&&!n&&a.current===i){if(p(!1),s){let t=i;return d.start(s,()=>{r.select(`open`)||a.current&&a.current!==t||e()}),()=>{(m.current||a.current!==t)&&d.clear()}}e()}},[n,i,a,o,s,c,l,d,r]),q(()=>{if(!n)return;let e=l.current,t=a.current;d.clear(),l.current={onOpenChange:r.setOpen,setIsInstantPhase:p},a.current=i,o.current={open:0,close:ko(c.current,`close`)},t!==null&&t!==i?(p(!0),e?.setIsInstantPhase(!0),e?.onOpenChange(!1,$(Wa))):(p(!1),e?.setIsInstantPhase(!1))},[n,i,r,a,o,c,l,d]),q(()=>()=>{if(a.current===i){if(l.current=null,!m.current)return;a.current=null,Po(o,c),d.clear()}},[l,a,o,i,c,d]),_.useMemo(()=>({hasProvider:u,delayRef:o,isInstantPhase:f}),[u,o,f])}function Lo(e,t,n,r){return e.addEventListener(t,n,r),()=>{e.removeEventListener(t,n,r)}}function Ro(...e){return()=>{for(let t=0;t<e.length;t+=1){let n=e[t];n&&n()}}}function zo(e){let t=_e(Bo,e).current;return t.next=e,q(t.effect),t}function Bo(e){let t={current:e,next:e,effect:()=>{t.current=t.next}};return t}var Vo={clipPath:`inset(50%)`,overflow:`hidden`,whiteSpace:`nowrap`,border:0,padding:0,width:1,height:1,margin:-1},Ho={...Vo,position:`fixed`,top:0,left:0},Uo={...Vo,position:`absolute`},Wo=_.forwardRef(function(e,t){let[n,r]=_.useState();q(()=>{Jr&&qr&&r(`button`)},[]);let i={tabIndex:0,role:n};return(0,Z.jsx)(`span`,{...e,ref:t,style:Ho,"aria-hidden":!n||void 0,...i,"data-base-ui-focus-guard":``})});function Go(e){return`data-base-ui-${e}`}var Ko=0;function qo(e,t={}){let{preventScroll:n=!1,sync:r=!1,shouldFocus:i}=t;cancelAnimationFrame(Ko);function a(){i&&!i()||e?.focus({preventScroll:n})}if(r)return a(),rt;let o=requestAnimationFrame(a);return Ko=o,()=>{Ko===o&&(cancelAnimationFrame(o),Ko=0)}}var Jo={inert:new WeakMap,"aria-hidden":new WeakMap},Yo=`data-base-ui-inert`,Xo={inert:new WeakSet,"aria-hidden":new WeakSet},Zo=new WeakMap,Qo=0;function $o(e){return Xo[e]}function es(e){return e?U(e)?e.host:es(e.parentNode):null}var ts=(e,t)=>t.map(t=>{if(e.contains(t))return t;let n=es(t);return e.contains(n)?n:null}).filter(e=>e!=null),ns=e=>{let t=new Set;return e.forEach(e=>{let n=e;for(;n&&!t.has(n);)t.add(n),n=n.parentNode}),t},rs=(e,t,n)=>{let r=[],i=e=>{!e||n.has(e)||Array.from(e.children).forEach(e=>{L(e)!==`script`&&(t.has(e)?i(e):r.push(e))})};return i(e),r};function is(e,t,n,r,{mark:i=!0}){let a=null;r?a=`inert`:n&&(a=`aria-hidden`);let o=null,s=null,c=ts(t,e),l=i?rs(t,ns(c),new Set(c)):[],u=[],d=[];if(a){let e=Jo[a],n=$o(a);s=n,o=e;let r=ts(t,Array.from(t.querySelectorAll(`[aria-live]`))),i=c.concat(r);rs(t,ns(i),new Set(i)).forEach(t=>{let r=t.getAttribute(a),i=r!==null&&r!==`false`,o=(e.get(t)||0)+1;e.set(t,o),u.push(t),o===1&&i&&n.add(t),i||t.setAttribute(a,a===`inert`?``:`true`)})}return i&&l.forEach(e=>{let t=(Zo.get(e)||0)+1;Zo.set(e,t),d.push(e),t===1&&e.setAttribute(Yo,``)}),Qo+=1,()=>{o&&u.forEach(e=>{let t=(o.get(e)||0)-1;o.set(e,t),t||(!s?.has(e)&&a&&e.removeAttribute(a),s?.delete(e))}),i&&d.forEach(e=>{let t=(Zo.get(e)||0)-1;Zo.set(e,t),t||e.removeAttribute(Yo)}),--Qo,Qo||(Jo.inert=new WeakMap,Jo[`aria-hidden`]=new WeakMap,Xo.inert=new WeakSet,Xo[`aria-hidden`]=new WeakSet,Zo=new WeakMap)}}function as(e,t={}){let{ariaHidden:n=!1,inert:r=!1,mark:i=!0}=t,a=Ue(e[0]).body;return is(e,a,n,r,{mark:i})}var os={style:{transition:`none`}},ss=`data-base-ui-click-trigger`,cs={fallbackAxisSide:`none`},ls={fallbackAxisSide:`end`},us={clipPath:`inset(50%)`,position:`fixed`,top:0,left:0},ds=_.createContext(null),fs=()=>_.useContext(ds),ps=Go(`portal`);function ms(e={}){let{ref:t,container:n,componentProps:r=at,elementProps:i}=e,a=Or(),o=fs()?.portalNode,[s,c]=_.useState(null),[l,u]=_.useState(null),d=K(e=>{e!==null&&u(e)}),f=_.useRef(null);q(()=>{if(n===null){f.current&&(f.current=null,u(null),c(null));return}let e=(n&&(B(n)?n:n.current))??o??document.body;if(e==null){f.current&&(f.current=null,u(null),c(null));return}f.current!==e&&(f.current=e,u(null),c(e))},[n,o]);let p=lt(`div`,r,{ref:[t,d],props:[{id:a,[ps]:``},i]}),m=s&&p?Pa.createPortal(p,s):null;return{node:l,nodeId:_.isValidElement(p)?p.props.id:void 0,subtree:m}}var hs=_.forwardRef(function(e,t){let{render:n,className:r,style:i,children:a,container:o,...s}=e,{node:c,nodeId:l,subtree:u}=ms({container:o,ref:t,componentProps:e,elementProps:s}),d=_.useRef(null),f=_.useRef(null),p=_.useRef(null),m=_.useRef(null),[h,g]=_.useState(null),v=_.useRef(!1),y=h?.modal,b=h?.open,x=!!h&&!h.modal&&h.open&&!!c;_.useEffect(()=>{if(!c||y)return;function e(e){c&&e.relatedTarget&&Sa(e)&&(e.type===`focusin`?v.current&&=(wa(c),!1):(Ca(c),v.current=!0))}return Ro(Lo(c,`focusin`,e,!0),Lo(c,`focusout`,e,!0))},[c,y]),q(()=>{!c||b!==!0||!v.current||(wa(c),v.current=!1)},[b,c]);let S=_.useMemo(()=>({beforeOutsideRef:d,afterOutsideRef:f,beforeInsideRef:p,afterInsideRef:m,portalNode:c,setFocusManagerState:g}),[c]);return(0,Z.jsxs)(_.Fragment,{children:[u,(0,Z.jsxs)(ds.Provider,{value:S,children:[x&&c&&(0,Z.jsx)(Wo,{"data-type":`outside`,ref:d,onFocus:e=>{Sa(e,c)?p.current?.focus():va(h?h.domReference:null)?.focus()}}),x&&c&&(0,Z.jsx)(`span`,{"aria-owns":l,style:us}),c&&Pa.createPortal(a,c),x&&c&&(0,Z.jsx)(Wo,{"data-type":`outside`,ref:f,onFocus:e=>{Sa(e,c)?m.current?.focus():(_a(h?h.domReference:null)?.focus(),h?.closeOnFocusOut&&h?.onOpenChange(!1,$(`focus-out`,e.nativeEvent)))}})]})]})});function gs(){let e=new Map;return{emit(t,n){e.get(t)?.forEach(e=>e(n))},on(t,n){e.has(t)||e.set(t,new Set),e.get(t).add(n)},off(t,n){e.get(t)?.delete(n)}}}var _s=class{nodesRef={current:[]};events=gs();addNode(e){this.nodesRef.current.push(e)}removeNode(e){let t=this.nodesRef.current.findIndex(t=>t===e);t!==-1&&this.nodesRef.current.splice(t,1)}},vs=_.createContext(null),ys=_.createContext(null),bs=()=>_.useContext(vs)?.id||null,xs=e=>{let t=_.useContext(ys);return e??t};function Ss(e){let t=Or(),n=xs(e),r=bs();return q(()=>{if(!t)return;let e={id:t,parentId:r};return n?.addNode(e),()=>{n?.removeNode(e)}},[n,t,r]),t}function Cs(e){let{children:t,id:n}=e,r=bs();return(0,Z.jsx)(vs.Provider,{value:_.useMemo(()=>({id:n,parentId:r}),[n,r]),children:t})}function ws(e){let{children:t,externalTree:n}=e,r=_e(()=>n??new _s).current;return(0,Z.jsx)(ys.Provider,{value:r,children:t})}function Ts(e,t){let n=R(ri(e));return e instanceof n.KeyboardEvent?`keyboard`:e instanceof n.FocusEvent?t||`keyboard`:`pointerType`in e?e.pointerType||`keyboard`:`touches`in e?`touch`:e instanceof n.MouseEvent?t||(e.detail===0?`keyboard`:`mouse`):``}var Es=20,Ds=[];function Os(){Ds=Ds.filter(e=>e.deref()?.isConnected)}function ks(e){Os(),e&&L(e)!==`body`&&(Ds.push(new WeakRef(e)),Ds.length>Es&&(Ds=Ds.slice(-20)))}function As(){return Os(),Ds[Ds.length-1]?.deref()}function js(e){return e?pa(e)?e:ha(e)[0]||e:null}function Ms(e){if(e.hasAttribute(`tabindex`)&&!e.hasAttribute(`data-tabindex`)||!e.getAttribute(`role`)?.includes(`dialog`))return;let t=ma(e).filter(e=>{let t=e.getAttribute(`data-tabindex`)||``;return pa(e)||e.hasAttribute(`data-tabindex`)&&!t.startsWith(`-`)}),n=e.getAttribute(`tabindex`);t.length===0?n!==`0`&&(e.setAttribute(`tabindex`,`0`),e.setAttribute(`data-tabindex`,`0`)):(n!==`-1`||e.hasAttribute(`data-tabindex`)&&e.getAttribute(`data-tabindex`)!==`-1`)&&(e.setAttribute(`tabindex`,`-1`),e.setAttribute(`data-tabindex`,`-1`))}function Ns(e){let{context:t,children:n,disabled:r=!1,initialFocus:i=!0,returnFocus:a=!0,restoreFocus:o=!1,modal:s=!0,closeOnFocusOut:c=!0,openInteractionType:l=``,nextFocusableElement:u,previousFocusableElement:d,beforeContentFocusGuardRef:f,externalTree:p,getInsideElements:m}=e,h=`rootStore`in t?t.rootStore:t,g=h.useState(`open`),v=h.useState(`domReferenceElement`),y=h.useState(`floatingElement`),{events:b,dataRef:x}=h.context,S=K(()=>x.current.floatingContext?.nodeId),C=i===!1,w=li(v)&&C,T=zo(i),E=zo(a),D=zo(l),O=zo(g),k=xs(p),A=fs(),j=_.useRef(!1),M=_.useRef(!1),N=_.useRef(!1),P=_.useRef(null),F=_.useRef(``),I=_.useRef(``),R=_.useRef(null),z=_.useRef(null),B=Je(R,f,A?.beforeInsideRef),V=Je(z,A?.afterInsideRef),U=Oa(),W=Oa(),ee=Ma(),te=A!=null,G=di(y),ne=K((e=G)=>e?ha(e):[]),re=K(()=>m?.().filter(e=>e!=null)??[]);_.useEffect(()=>{if(r||!s)return;function e(e){e.key===`Tab`&&Q(G,ni(Ue(G)))&&ne().length===0&&!w&&mi(e)}return Lo(Ue(G),`keydown`,e)},[r,G,s,w,ne]),_.useEffect(()=>{if(r||!g)return;let e=Ue(G);function t(){N.current=!1}function n(e){let t=ri(e),n=re(),r=Q(y,t)||Q(v,t)||Q(A?.portalNode,t)||n.some(e=>e===t||Q(e,t));N.current=!r,I.current=e.pointerType||`keyboard`,t?.closest(`[data-base-ui-click-trigger]`)&&(M.current=!0,W.start(0,()=>{M.current=!1}))}function i(){I.current=`keyboard`}return Ro(Lo(e,`pointerdown`,n,!0),Lo(e,`pointerup`,t,!0),Lo(e,`pointercancel`,t,!0),Lo(e,`keydown`,i,!0),t)},[r,y,v,G,g,A,W,re]),_.useEffect(()=>{if(r||!c)return;let e=Ue(G);function t(){M.current=!0,W.start(0,()=>{M.current=!1})}function n(e){let t=ri(e);pa(t)&&(P.current=t)}function i(t){let n=t.relatedTarget,r=t.currentTarget,i=ri(t);s&&n==null&&i!=null&&Q(y,i)&&ks(i),queueMicrotask(()=>{let a=S(),c=h.context.triggerElements,l=re(),f=n?.hasAttribute(Go(`focus-guard`))&&[R.current,z.current,A?.beforeInsideRef.current,A?.afterInsideRef.current,A?.beforeOutsideRef.current,A?.afterOutsideRef.current,Na(d),Na(u)].includes(n),p=!(Q(v,n)||Q(y,n)||Q(n,y)||Q(A?.portalNode,n)||l.some(e=>e===n||Q(e,n))||c.hasMatchingElement(e=>Q(e,n))||f||k&&(fi(k.nodesRef.current,a).find(e=>Q(e.context?.elements.floating,n)||Q(e.context?.elements.domReference,n))||pi(k.nodesRef.current,a).find(e=>[e.context?.elements.floating,di(e.context?.elements.floating)].includes(n)||e.context?.elements.domReference===n)));if(r===v&&G&&Ms(G),o&&r!==v&&!$i(i)&&ni(e)===e.body){if(H(G)&&(G.focus(),o===`popup`)){ee.request(()=>{G.focus()});return}let e=ne(),t=P.current,n=(t&&e.includes(t)?t:null)||e[e.length-1]||G;H(n)&&n.focus()}if(x.current.insideReactTree){x.current.insideReactTree=!1;return}(w||!s)&&n&&p&&!M.current&&(w||n!==As())&&(j.current=!0,h.setOpen(!1,$($a,t)))})}function a(){N.current||(x.current.insideReactTree=!0,U.start(0,()=>{x.current.insideReactTree=!1}))}let l=H(v)?v:null;if(!(!y&&!l))return Ro(l&&Lo(l,`focusout`,i),l&&Lo(l,`pointerdown`,t),y&&Lo(y,`focusin`,n),y&&Lo(y,`focusout`,i),y&&A&&Lo(y,`focusout`,a,!0))},[r,v,y,G,s,k,A,h,c,o,ne,w,S,x,U,W,ee,u,d,re]),_.useEffect(()=>{if(r||!y||!g)return;let e=Array.from(A?.portalNode?.querySelectorAll(`[${Go(`portal`)}]`)||[]),t=(k?pi(k.nodesRef.current,S()):[]).find(e=>li(e.context?.elements.domReference||null))?.context?.elements.domReference,n=as([y,...e,R.current,z.current,A?.beforeOutsideRef.current,A?.afterOutsideRef.current,...re(),t,Na(d),Na(u),w?v:null].filter(e=>e!=null),{ariaHidden:s||w,mark:!1}),i=as([y,...e].filter(e=>e!=null));return()=>{i(),n()}},[g,r,v,y,s,A,w,k,S,u,d,re]),q(()=>{if(!g||r||!H(G))return;F.current=``,I.current=``;let e=Ue(G),t=ni(e);queueMicrotask(()=>{let n=T.current,r=typeof n==`function`?n(D.current||``):n;if(r===void 0||r===!1||Q(G,t))return;let i=null,a=()=>(i??=ne(G),i[0]||G),o;o=r===!0||r===null?a():Na(r),o||=a();let s=Q(G,ni(e));qo(o,{preventScroll:o===G,shouldFocus(){if(!O.current)return!1;if(s)return!0;let t=ni(e);return!(t!==o&&Q(G,t))}})})},[r,g,G,ne,T,D,O]),q(()=>{if(r||!G)return;let e=Ue(G),t=ni(e),n=D.current==null;ks(t);function i(e){if(e.open||(F.current=Ts(e.nativeEvent,I.current)),e.reason===`trigger-hover`&&e.nativeEvent.type===`mouseleave`&&(j.current=!0),e.reason===`outside-press`){if(e.nested)j.current=!1;else if(gi(e.nativeEvent)||_i(e.nativeEvent))j.current=!1;else{let e=!1;Ue(G).createElement(`div`).focus({get preventScroll(){return e=!0,!1}}),e?j.current=!1:j.current=!0}}}b.on(`openchange`,i);function a(e){let r=E.current,i=typeof r==`function`?r(e):r;if(i===void 0||i===!1)return null;i===null&&(i=!0);let a=v?.isConnected?v:null,o=t?.isConnected&&L(t)!==`body`?t:null,s=n?o||a:a||o;return s||=As()||null,typeof i==`boolean`?s:Na(i)||s||null}return()=>{b.off(`openchange`,i);let t=ni(e),n=re(),r=Q(y,t)||n.some(e=>e===t||Q(e,t))||k&&fi(k.nodesRef.current,S(),!1).some(e=>Q(e.context?.elements.floating,t)),o=E.current,s=F.current,c=a(s);queueMicrotask(()=>{let n=js(c),i=typeof o!=`boolean`;if(o&&!j.current&&H(n)&&(!(!i&&n!==t&&t!==e.body)||r)){let e={preventScroll:!0};s===`keyboard`&&(e.focusVisible=!0),n.focus(e)}j.current=!1})}},[r,y,G,E,D,b,k,v,S,re]),q(()=>{if(!qr||g||!y)return;let e=ni(Ue(y));!H(e)||!si(e)||Q(y,e)&&e.blur()},[g,y]),q(()=>{if(!(r||!A))return A.setFocusManagerState({modal:s,closeOnFocusOut:c,open:g,onOpenChange:h.setOpen,domReference:v}),()=>{A.setFocusManagerState(null)}},[r,A,s,g,h,c,v]),q(()=>{if(!(r||!G))return Ms(G),()=>{queueMicrotask(Os)}},[r,G]);let ie=!r&&(!s||!w)&&(te||s);return(0,Z.jsxs)(_.Fragment,{children:[ie&&(0,Z.jsx)(Wo,{"data-type":`inside`,ref:B,onFocus:e=>{if(s){let e=ne();qo(e[e.length-1])}else A?.portalNode&&(j.current=!1,Sa(e,A.portalNode)?_a(v)?.focus():Na(d??A.beforeOutsideRef)?.focus())}}),n,ie&&(0,Z.jsx)(Wo,{"data-type":`inside`,ref:V,onFocus:e=>{s?qo(ne()[0]):A?.portalNode&&(c&&(j.current=!0),Sa(e,A.portalNode)?va(v)?.focus():Na(u??A.afterOutsideRef)?.focus())}})]})}function Ps(e,t={}){let{enabled:n=!0,event:r=`click`,toggle:i=!0,ignoreMouse:a=!1,stickIfOpen:o=!0,touchOpenDelay:s=0,reason:c=Ga}=t,l=`rootStore`in e?e.rootStore:e,u=l.context.dataRef,d=_.useRef(void 0),f=Ma(),p=Oa(),m=_.useMemo(()=>{function e(e,t,n,r){let i=$(c,t,n);e&&r===`touch`&&s>0?p.start(s,()=>{l.setOpen(!0,i)}):l.setOpen(e,i)}function t(e,t,n){let r=u.current.openEvent,a=l.select(`domReferenceElement`)!==t;return e&&a||!e||!i?!0:r&&o?!n(r.type):!1}return{onPointerDown(e){d.current=vi(e.pointerType,!0)&&_i(e.nativeEvent)?`virtual`:e.pointerType},onMouseDown(n){let i=d.current,o=n.nativeEvent,s=l.select(`open`);if(n.button!==0||r===`click`||vi(i,!0)&&a)return;let c=t(s,n.currentTarget,e=>e===`click`||e===`mousedown`),u=ri(o);if(si(u)){e(c,o,u,i);return}let p=n.currentTarget;f.request(()=>{e(c,o,p,i)})},onClick(n){if(r===`mousedown-only`)return;let i=d.current;if(r===`mousedown`&&i){d.current=void 0;return}vi(i,!0)&&a||e(t(l.select(`open`),n.currentTarget,e=>e===`click`||e===`mousedown`||e===`keydown`||e===`keyup`),n.nativeEvent,n.currentTarget,i)},onKeyDown(){d.current=void 0}}},[u,r,a,c,l,o,i,f,p,s]);return _.useMemo(()=>n?{reference:m}:at,[n,m])}function Fs(e,t){let n=null,r=null,i=!1;return{contextElement:e||void 0,getBoundingClientRect(){let a=e?.getBoundingClientRect()||{width:0,height:0,x:0,y:0},o=t.axis===`x`||t.axis===`both`,s=t.axis===`y`||t.axis===`both`,c=[`mouseenter`,`mousemove`].includes(t.dataRef.current.openEvent?.type||``)&&t.pointerType!==`touch`,l=a.width,u=a.height,d=a.x,f=a.y;return n==null&&t.x&&o&&(n=a.x-t.x),r==null&&t.y&&s&&(r=a.y-t.y),d-=n||0,f-=r||0,l=0,u=0,!i||c?(l=t.axis===`y`?a.width:0,u=t.axis===`x`?a.height:0,d=o&&t.x!=null?t.x:d,f=s&&t.y!=null?t.y:f):i&&!c&&(u=t.axis===`x`?a.height:u,l=t.axis===`y`?a.width:l),i=!0,{width:l,height:u,x:d,y:f,top:f,right:d+l,bottom:f+u,left:d}}}}function Is(e){return e!=null&&e.clientX!=null}function Ls(e,t={}){let{enabled:n=!0,axis:r=`both`}=t,i=`rootStore`in e?e.rootStore:e,a=i.useState(`open`),o=i.useState(`floatingElement`),s=i.useState(`domReferenceElement`),c=i.context.dataRef,l=_.useRef(!1),u=_.useRef(null),[d,f]=_.useState(),[p,m]=_.useState([]),h=K(e=>{i.set(`positionReference`,e)}),g=K((e,t,n)=>{l.current||c.current.openEvent&&!Is(c.current.openEvent)||i.set(`positionReference`,Fs(n??s,{x:e,y:t,axis:r,dataRef:c,pointerType:d}))}),v=K(e=>{a?u.current||(g(e.clientX,e.clientY,e.currentTarget),m([])):g(e.clientX,e.clientY,e.currentTarget)}),y=vi(d)?o:a;_.useEffect(()=>{if(!n){h(s);return}if(!y)return;function e(){u.current?.(),u.current=null}let t=R(o);function r(t){let n=ri(t);Q(o,n)?e():g(t.clientX,t.clientY)}return!c.current.openEvent||Is(c.current.openEvent)?u.current=Lo(t,`mousemove`,r):h(s),e},[y,n,o,c,s,i,g,h,p]),_.useEffect(()=>()=>{i.set(`positionReference`,null)},[i]),_.useEffect(()=>{n&&!o&&(l.current=!1)},[n,o]),_.useEffect(()=>{!n&&a&&(l.current=!0)},[n,a]);let b=_.useMemo(()=>{function e(e){f(e.pointerType)}return{onPointerDown:e,onPointerEnter:e,onMouseMove:v,onMouseEnter:v}},[v]);return _.useMemo(()=>n?{reference:b,trigger:b}:{},[n,b])}function Rs(){return!1}function zs(e){return{escapeKey:typeof e==`boolean`?e:e?.escapeKey??!1,outsidePress:typeof e==`boolean`?e:e?.outsidePress??!0}}function Bs(e,t={}){let{enabled:n=!0,escapeKey:r=!0,outsidePress:i=!0,outsidePressEvent:a=`sloppy`,referencePress:o=Rs,bubbles:s,externalTree:c}=t,l=`rootStore`in e?e.rootStore:e,u=l.useState(`open`),d=l.useState(`floatingElement`),{dataRef:f}=l.context,p=xs(c),m=K(typeof i==`function`?i:()=>!1),h=typeof i==`function`?m:i,g=h!==!1,v=K(()=>a),{escapeKey:y,outsidePress:b}=zs(s),x=_.useRef(!1),S=_.useRef(!1),C=_.useRef(!1),w=_.useRef(!1),T=_.useRef(``),E=_.useRef(null),D=Oa(),O=Oa(),k=K(()=>{O.clear(),f.current.insideReactTree=!1}),A=K(e=>{let t=f.current.floatingContext?.nodeId;return(p?fi(p.nodesRef.current,t):[]).some(t=>t.context?.open&&!t.context.dataRef.current[e])}),j=K(e=>ai(e,l.select(`floatingElement`))||ai(e,l.select(`domReferenceElement`))),M=K(e=>{o()&&l.setOpen(!1,$(Ga,e.nativeEvent))}),N=K(e=>{if(!u||!n||!r||e.key!==`Escape`||w.current||!y&&A(`__escapeKeyBubbles`))return;let t=$(eo,hi(e)?e.nativeEvent:e);l.setOpen(!1,t),t.isCanceled||e.preventDefault(),!y&&!t.isPropagationAllowed&&e.stopPropagation()}),P=K(()=>{f.current.insideReactTree=!0,O.start(0,k)}),F=K(e=>{if(!u||!n||e.button!==0)return;let t=ri(e.nativeEvent);Q(l.select(`floatingElement`),t)&&(x.current||(x.current=!0,S.current=!1))}),I=K(e=>{!u||!n||(e.defaultPrevented||e.nativeEvent.defaultPrevented)&&x.current&&(S.current=!0)});_.useEffect(()=>{if(!u||!n)return k;f.current.__escapeKeyBubbles=y,f.current.__outsidePressBubbles=b;let e=new Da,t=new Da;function i(){e.clear(),w.current=!0}function a(){e.start(qr?5:0,()=>{w.current=!1})}function o(){C.current=!0,t.start(0,()=>{C.current=!1})}function s(){x.current=!1,S.current=!1}function c(){let e=T.current,t=e===`pen`||!e?`mouse`:e,n=v(),r=typeof n==`function`?n():n;return typeof r==`string`?r:r[t]}function m(e){let t=c();return t===`intentional`&&e.type!==`click`||t===`sloppy`&&e.type===`click`}function _(e){let t=f.current.floatingContext?.nodeId,n=p&&fi(p.nodesRef.current,t).some(t=>ai(e,t.context?.elements.floating));return j(e)||n}function O(e){if(m(e)){e.type!==`click`&&!j(e)&&(t.clear(),C.current=!1),k();return}if(f.current.insideReactTree){k();return}let n=ri(e),r=`[${Go(`inert`)}]`,i=V(n)?n.getRootNode():null,a=Array.from((U(i)?i:Ue(l.select(`floatingElement`))).querySelectorAll(r)),o=l.context.triggerElements;if(n&&(o.hasElement(n)||o.hasMatchingElement(e=>Q(e,n))))return;let s=V(n)?n:null;for(;s&&!ce(s);){let e=de(s);if(ce(e)||!V(e))break;s=e}if(!(a.length&&V(n)&&!oi(n)&&!Q(n,l.select(`floatingElement`))&&a.every(e=>!Q(s,e)))){if(H(n)&&!(`touches`in e)){let t=ce(n),r=le(n),i=/auto|scroll/,a=t||i.test(r.overflowX),o=t||i.test(r.overflowY),s=a&&n.clientWidth>0&&n.scrollWidth>n.clientWidth,c=o&&n.clientHeight>0&&n.scrollHeight>n.clientHeight,l=r.direction===`rtl`,u=c&&(l?e.offsetX<=n.offsetWidth-n.clientWidth:e.offsetX>n.clientWidth),d=s&&e.offsetY>n.clientHeight;if(u||d)return}if(!_(e)){if(c()===`intentional`&&C.current){t.clear(),C.current=!1;return}typeof h==`function`&&!h(e)||A(`__outsidePressBubbles`)||(l.setOpen(!1,$(Ja,e)),k())}}}function M(e){c()!==`sloppy`||e.pointerType===`touch`||!l.select(`open`)||!n||j(e)||O(e)}function P(e){if(c()!==`sloppy`||!l.select(`open`)||!n||j(e))return;let t=e.touches[0];t&&(E.current={startTime:Date.now(),startX:t.clientX,startY:t.clientY,dismissOnTouchEnd:!1,dismissOnMouseDown:!0},D.start(1e3,()=>{E.current&&(E.current.dismissOnTouchEnd=!1,E.current.dismissOnMouseDown=!1)}))}function F(e,t){let n=ri(e);if(!n)return;let r=Lo(n,e.type,()=>{t(e),r()})}function I(e){T.current=`touch`,F(e,P)}function L(e){D.clear(),e.type===`pointerdown`&&(T.current=e.pointerType),!(e.type===`mousedown`&&E.current&&!E.current.dismissOnMouseDown)&&F(e,e=>{e.type===`pointerdown`?M(e):O(e)})}function R(e){if(!x.current)return;let n=S.current;if(s(),c()===`intentional`){if(e.type===`pointercancel`){n&&o();return}if(!_(e)){if(n){o();return}typeof h==`function`&&!h(e)||(t.clear(),C.current=!0,k())}}}function z(e){if(c()!==`sloppy`||!E.current||j(e))return;let t=e.touches[0];if(!t)return;let n=Math.abs(t.clientX-E.current.startX),r=Math.abs(t.clientY-E.current.startY),i=Math.sqrt(n*n+r*r);i>5&&(E.current.dismissOnTouchEnd=!0),i>10&&(O(e),D.clear(),E.current=null)}function B(e){F(e,z)}function W(e){c()!==`sloppy`||!E.current||j(e)||(E.current.dismissOnTouchEnd&&O(e),D.clear(),E.current=null)}function ee(e){F(e,W)}let te=Ue(d),G=Ro(r&&Ro(Lo(te,`keydown`,N),Lo(te,`compositionstart`,i),Lo(te,`compositionend`,a)),g&&Ro(Lo(te,`click`,L,!0),Lo(te,`pointerdown`,L,!0),Lo(te,`pointerup`,R,!0),Lo(te,`pointercancel`,R,!0),Lo(te,`mousedown`,L,!0),Lo(te,`mouseup`,R,!0),Lo(te,`touchstart`,I,!0),Lo(te,`touchmove`,B,!0),Lo(te,`touchend`,ee,!0)));return()=>{G(),e.clear(),t.clear(),s(),C.current=!1,k()}},[f,d,r,g,h,u,n,y,b,N,k,v,A,j,p,l,D]);let L=_.useMemo(()=>({onKeyDown:N,onPointerDown:M,onClick:M}),[N,M]),R=_.useMemo(()=>({onKeyDown:N,onPointerDown:I,onMouseDown:I,onClickCapture:P,onMouseDownCapture(e){P(),F(e)},onPointerDownCapture(e){P(),F(e)},onMouseUpCapture:P,onTouchEndCapture:P,onTouchMoveCapture:P}),[N,P,F,I]);return _.useMemo(()=>n?{reference:L,floating:R,trigger:L}:{},[n,L,R])}function Vs(e,t,n){let{reference:r,floating:i}=e,a=Mi(t),o=Ni(t),s=ji(o),c=Oi(t),l=a===`y`,u=r.x+r.width/2-i.width/2,d=r.y+r.height/2-i.height/2,f=r[s]/2-i[s]/2,p;switch(c){case`top`:p={x:u,y:r.y-i.height};break;case`bottom`:p={x:u,y:r.y+r.height};break;case`right`:p={x:r.x+r.width,y:d};break;case`left`:p={x:r.x-i.width,y:d};break;default:p={x:r.x,y:r.y}}let m=ki(t);return m&&(p[o]+=f*(m===`end`?1:-1)*(n&&l?-1:1)),p}async function Hs(e,t){t===void 0&&(t={});let{x:n,y:r,platform:i,rects:a,elements:o,strategy:s}=e,{boundary:c=`clippingAncestors`,rootBoundary:l=`viewport`,elementContext:u=`floating`,altBoundary:d=!1,padding:f=0}=Di(t,e),p=Gi(f),m=o[d?u===`floating`?`reference`:`floating`:u],h=Ki(await i.getClippingRect({element:await(i.isElement==null?void 0:i.isElement(m))??!0?m:m.contextElement||await(i.getDocumentElement==null?void 0:i.getDocumentElement(o.floating)),boundary:c,rootBoundary:l,strategy:s})),g=u===`floating`?{x:n,y:r,width:a.floating.width,height:a.floating.height}:a.reference,_=await(i.getOffsetParent==null?void 0:i.getOffsetParent(o.floating)),v=await(i.isElement==null?void 0:i.isElement(_))&&await(i.getScale==null?void 0:i.getScale(_))||{x:1,y:1},y=Ki(i.convertOffsetParentRelativeRectToViewportRelativeRect?await i.convertOffsetParentRelativeRectToViewportRelativeRect({elements:o,rect:g,offsetParent:_,strategy:s}):g);return{top:(h.top-y.top+p.top)/v.y,bottom:(y.bottom-h.bottom+p.bottom)/v.y,left:(h.left-y.left+p.left)/v.x,right:(y.right-h.right+p.right)/v.x}}var Us=50,Ws=async(e,t,n)=>{let{placement:r=`bottom`,strategy:i=`absolute`,middleware:a=[],platform:o}=n,s=o.detectOverflow?o:{...o,detectOverflow:Hs},c=await(o.isRTL==null?void 0:o.isRTL(t)),l=await o.getElementRects({reference:e,floating:t,strategy:i}),{x:u,y:d}=Vs(l,r,c),f=r,p=0,m={};for(let n=0;n<a.length;n++){let h=a[n];if(!h)continue;let{name:g,fn:_}=h,{x:v,y,data:b,reset:x}=await _({x:u,y:d,initialPlacement:r,placement:f,strategy:i,middlewareData:m,rects:l,platform:s,elements:{reference:e,floating:t}});u=v??u,d=y??d,m[g]={...m[g],...b},x&&p<Us&&(p++,typeof x==`object`&&(x.placement&&(f=x.placement),x.rects&&(l=x.rects===!0?await o.getElementRects({reference:e,floating:t,strategy:i}):x.rects),{x:u,y:d}=Vs(l,f,c)),n=-1)}return{x:u,y:d,placement:f,strategy:i,middlewareData:m}},Gs=function(e){return e===void 0&&(e={}),{name:`flip`,options:e,async fn(t){var n;let{placement:r,middlewareData:i,rects:a,initialPlacement:o,platform:s,elements:c}=t,{mainAxis:l=!0,crossAxis:u=!0,fallbackPlacements:d,fallbackStrategy:f=`bestFit`,fallbackAxisSideDirection:p=`none`,flipAlignment:m=!0,...h}=Di(e,t);if((n=i.arrow)!=null&&n.alignmentOffset)return{};let g=Oi(r),_=Mi(o),v=Oi(o)===o,y=await(s.isRTL==null?void 0:s.isRTL(c.floating)),b=d||(v||!m?[Ui(o)]:Fi(o)),x=p!==`none`;!d&&x&&b.push(...Hi(o,m,p,y));let S=[o,...b],C=await s.detectOverflow(t,h),w=[],T=i.flip?.overflows||[];if(l&&w.push(C[g]),u){let e=Pi(r,a,y);w.push(C[e[0]],C[e[1]])}if(T=[...T,{placement:r,overflows:w}],!w.every(e=>e<=0)){let e=(i.flip?.index||0)+1,t=S[e];if(t&&(u!==`alignment`||_===Mi(t)||T.every(e=>Mi(e.placement)!==_||e.overflows[0]>0)))return{data:{index:e,overflows:T},reset:{placement:t}};let n=T.filter(e=>e.overflows[0]<=0).sort((e,t)=>e.overflows[1]-t.overflows[1])[0]?.placement;if(!n)switch(f){case`bestFit`:{let e=T.filter(e=>{if(x){let t=Mi(e.placement);return t===_||t===`y`}return!0}).map(e=>[e.placement,e.overflows.filter(e=>e>0).reduce((e,t)=>e+t,0)]).sort((e,t)=>e[1]-t[1])[0]?.[0];e&&(n=e);break}case`initialPlacement`:n=o}if(r!==n)return{reset:{placement:n}}}return{}}}},Ks=new Set([`left`,`top`]);async function qs(e,t){let{placement:n,platform:r,elements:i}=e,a=await(r.isRTL==null?void 0:r.isRTL(i.floating)),o=Oi(n),s=ki(n),c=Mi(n)===`y`,l=Ks.has(o)?-1:1,u=a&&c?-1:1,d=Di(t,e),{mainAxis:f,crossAxis:p,alignmentAxis:m}=typeof d==`number`?{mainAxis:d,crossAxis:0,alignmentAxis:null}:{mainAxis:d.mainAxis||0,crossAxis:d.crossAxis||0,alignmentAxis:d.alignmentAxis};return s&&typeof m==`number`&&(p=s===`end`?m*-1:m),c?{x:p*u,y:f*l}:{x:f*l,y:p*u}}var Js=function(e){return e===void 0&&(e=0),{name:`offset`,options:e,async fn(t){var n;let{x:r,y:i,placement:a,middlewareData:o}=t,s=await qs(t,e);return a===o.offset?.placement&&(n=o.arrow)!=null&&n.alignmentOffset?{}:{x:r+s.x,y:i+s.y,data:{...s,placement:a}}}}},Ys=function(e){return e===void 0&&(e={}),{name:`shift`,options:e,async fn(t){let{x:n,y:r,placement:i,platform:a}=t,{mainAxis:o=!0,crossAxis:s=!1,limiter:c={fn:e=>{let{x:t,y:n}=e;return{x:t,y:n}}},...l}=Di(e,t),u={x:n,y:r},d=await a.detectOverflow(t,l),f=Mi(i),p=Ai(f),m=u[p],h=u[f],g=(e,t)=>Ei(t+d[e===`y`?`top`:`left`],t,t-d[e===`y`?`bottom`:`right`]);o&&(m=g(p,m)),s&&(h=g(f,h));let _=c.fn({...t,[p]:m,[f]:h});return{..._,data:{x:_.x-n,y:_.y-r,enabled:{[p]:o,[f]:s}}}}}},Xs=function(e){return e===void 0&&(e={}),{options:e,fn(t){let{x:n,y:r,placement:i,rects:a,middlewareData:o}=t,{offset:s=0,mainAxis:c=!0,crossAxis:l=!0}=Di(e,t),u={x:n,y:r},d=Mi(i),f=Ai(d),p=u[f],m=u[d],h=Di(s,t),g=typeof h==`number`?{mainAxis:h,crossAxis:0}:{mainAxis:h.mainAxis??0,crossAxis:h.crossAxis??0};if(c){let e=f===`y`?`height`:`width`,t=a.reference[f]-a.floating[e]+g.mainAxis,n=a.reference[f]+a.reference[e]-g.mainAxis;p<t?p=t:p>n&&(p=n)}if(l){let e=f===`y`?`width`:`height`,t=Ks.has(Oi(i)),n=a.reference[d]-a.floating[e]+(t&&o.offset?.[d]||0)+(t?0:g.crossAxis),r=a.reference[d]+a.reference[e]+(t?0:o.offset?.[d]||0)-(t?g.crossAxis:0);m<n?m=n:m>r&&(m=r)}return{[f]:p,[d]:m}}}},Zs=function(e){return e===void 0&&(e={}),{name:`size`,options:e,async fn(t){let{placement:n,rects:r,platform:i,elements:a}=t,{apply:o=()=>{},...s}=Di(e,t),c=await i.detectOverflow(t,s),l=Oi(n),u=ki(n),d=Mi(n)===`y`,{width:f,height:p}=r.floating,m,h;l===`top`||l===`bottom`?(m=l,h=u===(await(i.isRTL==null?void 0:i.isRTL(a.floating))?`start`:`end`)?`left`:`right`):(h=l,m=u===`end`?`top`:`bottom`);let g=p-c.top-c.bottom,_=f-c.left-c.right,v=bi(p-c[m],g),y=bi(f-c[h],_),b=t.middlewareData.shift,x=!b,S=v,C=y;b!=null&&b.enabled.x&&(C=_),b!=null&&b.enabled.y&&(S=g),x&&!u&&(d?C=f-2*xi(c.left,c.right):S=p-2*xi(c.top,c.bottom)),await o({...t,availableWidth:C,availableHeight:S});let w=await i.getDimensions(a.floating);return f!==w.width||p!==w.height?{reset:{rects:!0}}:{}}}};function Qs(e){let t=le(e),n=parseFloat(t.width)||0,r=parseFloat(t.height)||0,i=H(e),a=i?e.offsetWidth:n,o=i?e.offsetHeight:r,s=Si(n)!==a||Si(r)!==o;return s&&(n=a,r=o),{width:n,height:r,$:s}}function $s(e){return V(e)?e:e.contextElement}function ec(e){let t=$s(e);if(!H(t))return wi(1);let n=t.getBoundingClientRect(),{width:r,height:i,$:a}=Qs(t),o=(a?Si(n.width):n.width)/r,s=(a?Si(n.height):n.height)/i;return(!o||!Number.isFinite(o))&&(o=1),(!s||!Number.isFinite(s))&&(s=1),{x:o,y:s}}var tc=wi(0);function nc(e){let t=R(e);return!se()||!t.visualViewport?tc:{x:t.visualViewport.offsetLeft,y:t.visualViewport.offsetTop}}function rc(e,t,n){return t===void 0&&(t=!1),!!n&&t&&n===R(e)}function ic(e,t,n,r){t===void 0&&(t=!1),n===void 0&&(n=!1);let i=e.getBoundingClientRect(),a=$s(e),o=wi(1);t&&(r?V(r)&&(o=ec(r)):o=ec(e));let s=rc(a,n,r)?nc(a):wi(0),c=(i.left+s.x)/o.x,l=(i.top+s.y)/o.y,u=i.width/o.x,d=i.height/o.y;if(a&&r){let e=R(a),t=V(r)?R(r):r,n=e,i=me(n);for(;i&&t!==n;){let e=ec(i),t=i.getBoundingClientRect(),r=le(i),a=t.left+(i.clientLeft+parseFloat(r.paddingLeft))*e.x,o=t.top+(i.clientTop+parseFloat(r.paddingTop))*e.y;c*=e.x,l*=e.y,u*=e.x,d*=e.y,c+=a,l+=o,n=R(i),i=me(n)}}return Ki({width:u,height:d,x:c,y:l})}function ac(e,t){let n=ue(e).scrollLeft;return t?t.left+n:ic(z(e)).left+n}function oc(e,t){let n=e.getBoundingClientRect();return{x:n.left+t.scrollLeft-ac(e,n),y:n.top+t.scrollTop}}function sc(e){let{elements:t,rect:n,offsetParent:r,strategy:i}=e,a=i===`fixed`,o=z(r),s=t?te(t.floating):!1;if(r===o||s&&a)return n;let c={scrollLeft:0,scrollTop:0},l=wi(1),u=wi(0),d=H(r);if((d||!a)&&((L(r)!==`body`||W(o))&&(c=ue(r)),d)){let e=ic(r);l=ec(r),u.x=e.x+r.clientLeft,u.y=e.y+r.clientTop}let f=o&&!d&&!a?oc(o,c):wi(0);return{width:n.width*l.x,height:n.height*l.y,x:n.x*l.x-c.scrollLeft*l.x+u.x+f.x,y:n.y*l.y-c.scrollTop*l.y+u.y+f.y}}function cc(e){return e.getClientRects?Array.from(e.getClientRects()):[]}function lc(e){let t=ue(e),n=e.ownerDocument.body,r=xi(e.scrollWidth,e.clientWidth,n.scrollWidth,n.clientWidth),i=xi(e.scrollHeight,e.clientHeight,n.scrollHeight,n.clientHeight),a=-t.scrollLeft+ac(e),o=-t.scrollTop;return le(n).direction===`rtl`&&(a+=xi(e.clientWidth,n.clientWidth)-r),{width:r,height:i,x:a,y:o}}var uc=25;function dc(e,t,n){n===void 0&&(n=`viewport`);let r=n===`layoutViewport`,i=R(e),a=z(e),o=i.visualViewport,s=a.clientWidth,c=a.clientHeight,l=0,u=0;if(o){let e=!se()||t===`fixed`;r?e||(l=-o.offsetLeft,u=-o.offsetTop):(s=o.width,c=o.height,e&&(l=o.offsetLeft,u=o.offsetTop))}if(ac(a)<=0){let e=a.ownerDocument,t=e.body,n=getComputedStyle(t),r=e.compatMode===`CSS1Compat`&&parseFloat(n.marginLeft)+parseFloat(n.marginRight)||0,i=Math.abs(a.clientWidth-t.clientWidth-r),o=getComputedStyle(a).scrollbarGutter===`stable both-edges`?i/2:i;o<=uc&&(s-=o)}return{width:s,height:c,x:l,y:u}}function fc(e,t){let n=ic(e,!0,t===`fixed`),r=n.top+e.clientTop,i=n.left+e.clientLeft,a=ec(e);return{width:e.clientWidth*a.x,height:e.clientHeight*a.y,x:i*a.x,y:r*a.y}}function pc(e,t,n){let r;if(t===`viewport`||t===`layoutViewport`)r=dc(e,n,t);else if(t===`document`)r=lc(z(e));else if(V(t))r=fc(t,n);else{let n=nc(e);r={x:t.x-n.x,y:t.y-n.y,width:t.width,height:t.height}}return Ki(r)}function mc(e,t){let n=t.get(e);if(n)return n;let r=pe(e,[],!1).filter(e=>V(e)&&L(e)!==`body`),i=null,a=le(e).position===`fixed`,o=a?de(e):e;for(;V(o)&&!ce(o);){let e=le(o),t=ae(o),n=i?i.position:a?`fixed`:``;!t&&(n===`fixed`||n===`absolute`&&e.position===`static`)?r=r.filter(e=>e!==o):i=e,o=de(o)}return t.set(e,r),r}function hc(e){let{element:t,boundary:n,rootBoundary:r,strategy:i}=e,a=[...n===`clippingAncestors`?te(t)?[]:mc(t,this._c):[].concat(n),r],o=pc(t,a[0],i),s=o.top,c=o.right,l=o.bottom,u=o.left;for(let e=1;e<a.length;e++){let n=pc(t,a[e],i);s=xi(n.top,s),c=bi(n.right,c),l=bi(n.bottom,l),u=xi(n.left,u)}return{width:c-u,height:l-s,x:u,y:s}}function gc(e){let{width:t,height:n}=Qs(e);return{width:t,height:n}}function _c(e,t,n){let r=H(t),i=z(t),a=n===`fixed`,o=ic(e,!0,a,t),s={scrollLeft:0,scrollTop:0},c=wi(0);if((r||!a)&&((L(t)!==`body`||W(i))&&(s=ue(t)),r)){let e=ic(t,!0,a,t);c.x=e.x+t.clientLeft,c.y=e.y+t.clientTop}!r&&i&&(c.x=ac(i));let l=i&&!r&&!a?oc(i,s):wi(0);return{x:o.left+s.scrollLeft-c.x-l.x,y:o.top+s.scrollTop-c.y-l.y,width:o.width,height:o.height}}function vc(e){return le(e).position===`static`}function yc(e,t){if(!H(e)||le(e).position===`fixed`)return null;if(t)return t(e);let n=e.offsetParent;return z(e)===n&&(n=n.ownerDocument.body),n}function bc(e,t){let n=R(e);if(te(e))return n;if(!H(e)){let t=de(e);for(;t&&!ce(t);){if(V(t)&&!vc(t))return t;t=de(t)}return n}let r=yc(e,t);for(;r&&ee(r)&&vc(r);)r=yc(r,t);return r&&ce(r)&&vc(r)&&!ae(r)?n:r||oe(e)||n}var xc=async function(e){let t=this.getOffsetParent||bc,n=this.getDimensions,r=await n(e.floating);return{reference:_c(e.reference,await t(e.floating),e.strategy),floating:{x:0,y:0,width:r.width,height:r.height}}};function Sc(e){return le(e).direction===`rtl`}var Cc={convertOffsetParentRelativeRectToViewportRelativeRect:sc,getDocumentElement:z,getClippingRect:hc,getOffsetParent:bc,getElementRects:xc,getClientRects:cc,getDimensions:gc,getScale:ec,isElement:V,isRTL:Sc};function wc(e,t){return e.x===t.x&&e.y===t.y&&e.width===t.width&&e.height===t.height}function Tc(e,t,n){let r=null,i,a=z(e);function o(){var e;clearTimeout(i),(e=r)==null||e.disconnect(),r=null}function s(n,c){n===void 0&&(n=!1),c===void 0&&(c=1),o();let l=e.getBoundingClientRect(),{left:u,top:d,width:f,height:p}=l;if(n||t(),!f||!p)return;let m=Ci(d),h=Ci(a.clientWidth-(u+f)),g=Ci(a.clientHeight-(d+p)),_=Ci(u),v={rootMargin:-m+`px `+-h+`px `+-g+`px `+-_+`px`,threshold:xi(0,bi(1,c))||1},y=!0;function b(t){let n=t[0].intersectionRatio;if(!wc(l,e.getBoundingClientRect()))return s();if(n!==c){if(!y)return s();n?s(!1,n):i=setTimeout(()=>{s(!1,1e-7)},1e3)}y=!1}try{r=new IntersectionObserver(b,{...v,root:a.ownerDocument})}catch{r=new IntersectionObserver(b,v)}r.observe(e)}let c=R(e),l=()=>s(n);return c.addEventListener(`resize`,l),s(!0),()=>{c.removeEventListener(`resize`,l),o()}}function Ec(e,t,n,r){r===void 0&&(r={});let{ancestorScroll:i=!0,ancestorResize:a=!0,elementResize:o=typeof ResizeObserver==`function`,layoutShift:s=typeof IntersectionObserver==`function`,animationFrame:c=!1}=r,l=$s(e),u=i||a?[...l?pe(l):[],...t?pe(t):[]]:[];u.forEach(e=>{i&&e.addEventListener(`scroll`,n),a&&e.addEventListener(`resize`,n)});let d=l&&s?Tc(l,n,a):null,f=-1,p=null;o&&(p=new ResizeObserver(e=>{let[r]=e;r&&r.target===l&&p&&t&&(p.unobserve(t),cancelAnimationFrame(f),f=requestAnimationFrame(()=>{var e;(e=p)==null||e.observe(t)})),n()}),l&&!c&&p.observe(l),t&&p.observe(t));let m,h=c?ic(e):null;c&&g();function g(){let t=ic(e);h&&!wc(h,t)&&n(),h=t,m=requestAnimationFrame(g)}return n(),()=>{var e;u.forEach(e=>{i&&e.removeEventListener(`scroll`,n),a&&e.removeEventListener(`resize`,n)}),d?.(),(e=p)==null||e.disconnect(),p=null,c&&cancelAnimationFrame(m)}}var Dc=Js,Oc=Ys,kc=Gs,Ac=Zs,jc=Xs,Mc=(e,t,n)=>{let r=new Map,i=n??{},a={...Cc,...i.platform,_c:r};return Ws(e,t,{...i,platform:a})},Nc=typeof document<`u`?_.useLayoutEffect:function(){};function Pc(e,t){if(e===t)return!0;if(typeof e!=typeof t)return!1;if(typeof e==`function`&&e.toString()===t.toString())return!0;let n,r,i;if(e&&t&&typeof e==`object`){if(Array.isArray(e)){if(n=e.length,n!==t.length)return!1;for(r=n;r--!==0;)if(!Pc(e[r],t[r]))return!1;return!0}if(i=Object.keys(e),n=i.length,n!==Object.keys(t).length)return!1;for(r=n;r--!==0;)if(!{}.hasOwnProperty.call(t,i[r]))return!1;for(r=n;r--!==0;){let n=i[r];if(!(n===`_owner`&&e.$$typeof)&&!Pc(e[n],t[n]))return!1}return!0}return e!==e&&t!==t}function Fc(e){return typeof window>`u`?1:(e.ownerDocument.defaultView||window).devicePixelRatio||1}function Ic(e,t){let n=Fc(e);return Math.round(t*n)/n}function Lc(e){let t=_.useRef(e);return Nc(()=>{t.current=e}),t}function Rc(e){e===void 0&&(e={});let{placement:t=`bottom`,strategy:n=`absolute`,middleware:r=[],platform:i,elements:{reference:a,floating:o}={},transform:s=!0,whileElementsMounted:c,open:l}=e,[u,d]=_.useState({x:0,y:0,strategy:n,placement:t,middlewareData:{},isPositioned:!1}),[f,p]=_.useState(r);Pc(f,r)||p(r);let[m,h]=_.useState(null),[g,v]=_.useState(null),y=_.useCallback(e=>{e!==C.current&&(C.current=e,h(e))},[]),b=_.useCallback(e=>{e!==w.current&&(w.current=e,v(e))},[]),x=a||m,S=o||g,C=_.useRef(null),w=_.useRef(null),T=_.useRef(u),E=c!=null,D=Lc(c),O=Lc(i),k=Lc(l),A=_.useCallback(()=>{if(!C.current||!w.current)return;let e={placement:t,strategy:n,middleware:f};O.current&&(e.platform=O.current),Mc(C.current,w.current,e).then(e=>{let t={...e,isPositioned:k.current!==!1};j.current&&!Pc(T.current,t)&&(T.current=t,Pa.flushSync(()=>{d(t)}))})},[f,t,n,O,k]);Nc(()=>{l===!1&&T.current.isPositioned&&(T.current.isPositioned=!1,d(e=>({...e,isPositioned:!1})))},[l]);let j=_.useRef(!1);Nc(()=>(j.current=!0,()=>{j.current=!1}),[]),Nc(()=>{if(x&&(C.current=x),S&&(w.current=S),x&&S){if(D.current)return D.current(x,S,A);A()}},[x,S,A,D,E]);let M=_.useMemo(()=>({reference:C,floating:w,setReference:y,setFloating:b}),[y,b]),N=_.useMemo(()=>({reference:x,floating:S}),[x,S]),P=_.useMemo(()=>{let e={position:n,left:0,top:0};if(!N.floating)return e;let t=Ic(N.floating,u.x),r=Ic(N.floating,u.y);return s?{...e,transform:`translate(`+t+`px, `+r+`px)`,...Fc(N.floating)>=1.5&&{willChange:`transform`}}:{position:n,left:t,top:r}},[n,s,N.floating,u.x,u.y]);return _.useMemo(()=>({...u,update:A,refs:M,elements:N,floatingStyles:P}),[u,A,M,N,P])}var zc=(e,t)=>{let n=Dc(e);return{name:n.name,fn:n.fn,options:[e,t]}},Bc=(e,t)=>{let n=Oc(e);return{name:n.name,fn:n.fn,options:[e,t]}},Vc=(e,t)=>({fn:jc(e).fn,options:[e,t]}),Hc=(e,t)=>{let n=kc(e);return{name:n.name,fn:n.fn,options:[e,t]}},Uc=(e,t)=>{let n=Ac(e);return{name:n.name,fn:n.fn,options:[e,t]}},Wc=o((e=>{var t=u();function n(e,t){return e===t&&(e!==0||1/e==1/t)||e!==e&&t!==t}var r=typeof Object.is==`function`?Object.is:n,i=t.useState,a=t.useEffect,o=t.useLayoutEffect,s=t.useDebugValue;function c(e,t){var n=t(),r=i({inst:{value:n,getSnapshot:t}}),c=r[0].inst,u=r[1];return o(function(){c.value=n,c.getSnapshot=t,l(c)&&u({inst:c})},[e,n,t]),a(function(){return l(c)&&u({inst:c}),e(function(){l(c)&&u({inst:c})})},[e]),s(n),n}function l(e){var t=e.getSnapshot;e=e.value;try{var n=t();return!r(e,n)}catch{return!0}}function d(e,t){return t()}var f=typeof window>`u`||window.document===void 0||window.document.createElement===void 0?d:c;e.useSyncExternalStore=t.useSyncExternalStore===void 0?f:t.useSyncExternalStore})),Gc=o(((e,t)=>{t.exports=Wc()})),Kc=o((e=>{var t=u(),n=Gc();function r(e,t){return e===t&&(e!==0||1/e==1/t)||e!==e&&t!==t}var i=typeof Object.is==`function`?Object.is:r,a=n.useSyncExternalStore,o=t.useRef,s=t.useEffect,c=t.useMemo,l=t.useDebugValue;e.useSyncExternalStoreWithSelector=function(e,t,n,r,u){var d=o(null);if(d.current===null){var f={hasValue:!1,value:null};d.current=f}else f=d.current;d=c(function(){function e(e){if(!a){if(a=!0,o=e,e=r(e),u!==void 0&&f.hasValue){var t=f.value;if(u(t,e))return s=t}return s=e}if(t=s,i(o,e))return t;var n=r(e);return u!==void 0&&u(t,n)?(o=e,t):(o=e,s=n)}var a=!1,o,s,c=n===void 0?null:n;return[function(){return e(t())},c===null?void 0:function(){return e(c())}]},[t,n,r,u]);var p=a(e,d[0],d[1]);return s(function(){f.hasValue=!0,f.value=p},[p]),l(p),p}})),qc=o(((e,t)=>{t.exports=Kc()})),Jc=Gc(),Yc=qc(),Xc=tt(19)?$c:el;function Zc(e,t,n,r,i){return Xc(e,t,n,r,i)}function Qc(e,t,n,r,i){let a=_.useCallback(()=>t(e.getSnapshot(),n,r,i),[e,t,n,r,i]);return(0,Jc.useSyncExternalStore)(e.subscribe,a,a)}So({before(e){e.syncIndex=0,e.didInitialize||(e.syncTick=1,e.syncHooks=[],e.didChangeStore=!0,e.getSnapshot=()=>{let t=!1;for(let n=0;n<e.syncHooks.length;n+=1){let r=e.syncHooks[n],i=r.selector(r.store.state,r.a1,r.a2,r.a3);Object.is(r.value,i)||(t=!0,r.value=i)}return t&&(e.syncTick+=1),e.syncTick})},after(e){e.syncHooks.length>0&&(e.didChangeStore&&(e.didChangeStore=!1,e.subscribe=t=>{let n=new Set;for(let t of e.syncHooks)n.add(t.store);let r=[];for(let e of n)r.push(e.subscribe(t));return()=>{for(let e of r)e()}}),(0,Jc.useSyncExternalStore)(e.subscribe,e.getSnapshot,e.getSnapshot))}});function $c(e,t,n,r,i){let a=xo();if(!a)return Qc(e,t,n,r,i);let o=a.syncIndex;a.syncIndex+=1;let s;return a.didInitialize?(s=a.syncHooks[o],(s.store!==e||s.selector!==t||!Object.is(s.a1,n)||!Object.is(s.a2,r)||!Object.is(s.a3,i))&&(s.store!==e&&(a.didChangeStore=!0),s.store=e,s.selector=t,s.a1=n,s.a2=r,s.a3=i,s.value=t(e.getSnapshot(),n,r,i))):(s={store:e,selector:t,a1:n,a2:r,a3:i,value:t(e.getSnapshot(),n,r,i)},a.syncHooks.push(s)),s.value}function el(e,t,n,r,i){return(0,Yc.useSyncExternalStoreWithSelector)(e.subscribe,e.getSnapshot,e.getSnapshot,e=>t(e,n,r,i))}var tl=class{constructor(e){this.state=e,this.listeners=new Set,this.updateTick=0}subscribe=e=>(this.listeners.add(e),()=>{this.listeners.delete(e)});getSnapshot=()=>this.state;setState(e){if(this.state===e)return;this.state=e,this.updateTick+=1;let t=this.updateTick;for(let n of this.listeners){if(t!==this.updateTick)return;n(e)}}update(e){for(let t in e)if(!Object.is(this.state[t],e[t])){this.setState({...this.state,...e});return}}set(e,t){Object.is(this.state[e],t)||this.setState({...this.state,[e]:t})}notifyAll(){let e={...this.state};this.setState(e)}use(e,t,n,r){return Zc(this,e,t,n,r)}},nl=class extends tl{constructor(e,t={},n){super(e),this.context=t,this.selectors=n}useSyncedValue(e,t){_.useDebugValue(e);let n=this;q(()=>{n.state[e]!==t&&n.set(e,t)},[n,e,t])}useSyncedValueWithCleanup(e,t){let n=this;q(()=>(n.state[e]!==t&&n.set(e,t),()=>{n.set(e,void 0)}),[n,e,t])}useSyncedValues(e){let t=this;q(()=>{t.update(e)},[t,...Object.values(e)])}useControlledProp(e,t){_.useDebugValue(e);let n=this,r=t!==void 0;q(()=>{r&&!Object.is(n.state[e],t)&&n.setState({...n.state,[e]:t})},[n,e,t,r])}select(e,t,n,r){let i=this.selectors[e];return i(this.state,t,n,r)}useState(e,t,n,r){return _.useDebugValue(e),Zc(this,this.selectors[e],t,n,r)}useContextCallback(e,t){_.useDebugValue(e);let n=K(t??rt);this.context[e]=n}useStateSetter(e){let t=_.useRef(void 0);return t.current===void 0&&(t.current=t=>{this.set(e,t)}),t.current}observe(e,t){let n;n=typeof e==`function`?e:this.selectors[e];let r=n(this.state);return t(r,r,this),this.subscribe(e=>{let i=n(e);if(!Object.is(r,i)){let e=r;r=i,t(i,e,this)}})}},rl={open:e=>e.open,transitionStatus:e=>e.transitionStatus,domReferenceElement:e=>e.domReferenceElement,referenceElement:e=>e.positionReference??e.referenceElement,floatingElement:e=>e.floatingElement,floatingId:e=>e.floatingId},il=class extends nl{constructor(e){let{syncOnly:t,nested:n,onOpenChange:r,triggerElements:i,...a}=e;super({...a,positionReference:a.referenceElement,domReferenceElement:a.referenceElement},{onOpenChange:r,dataRef:{current:{}},events:gs(),nested:n,triggerElements:i},rl),this.syncOnly=t}syncOpenEvent=(e,t)=>{(!e||!this.state.open||t!=null&&yi(t))&&(this.context.dataRef.current.openEvent=e?t:void 0)};dispatchOpenChange=(e,t)=>{this.syncOpenEvent(e,t.event);let n={open:e,reason:t.reason,nativeEvent:t.event,nested:this.context.nested,triggerElement:t.trigger};this.context.events.emit(`openchange`,n)};setOpen=(e,t)=>{if(this.syncOnly){this.context.onOpenChange?.(e,t);return}this.dispatchOpenChange(e,t),this.context.onOpenChange?.(e,t)}};function al(e){let{popupStore:t,treatPopupAsFloatingElement:n=!1,floatingRootContext:r,floatingId:i,nested:a,onOpenChange:o}=e,s=t.useState(`open`),c=t.useState(`activeTriggerElement`),l=t.useState(n?`popupElement`:`positionerElement`),u=t.context.triggerElements,d=o,f=_.useRef(null);r===void 0&&f.current===null&&(f.current=new il({open:s,transitionStatus:void 0,referenceElement:c,floatingElement:l,triggerElements:u,onOpenChange:d,floatingId:i,syncOnly:!0,nested:a}));let p=r??f.current;return t.useSyncedValue(`floatingId`,i),q(()=>{let e={open:s,floatingId:i,referenceElement:c,floatingElement:l};V(c)&&(e.domReferenceElement=c),p.state.positionReference===p.state.referenceElement&&(e.positionReference=c),p.update(e)},[s,i,c,l,p]),p.context.onOpenChange=d,p.context.nested=a,p}var ol={tabIndex:-1,[Xr]:``};function sl(e){return t=>t!==`touch`||e.current}function cl(e,t=!1){let n=Or(),r=bs()!=null,i=_e(()=>e(n,r)).current;return al({popupStore:i,treatPopupAsFloatingElement:t,floatingRootContext:i.state.floatingRootContext,floatingId:n,nested:r,onOpenChange:i.setOpen}),i}function ll({handle:e,store:t}){return q(()=>e.attachStore(t),[e,t]),null}function ul(e,t){let n=_.useRef(null),r=_.useRef(null);return _.useCallback(i=>{if(e===void 0)return;let a=!1;if(n.current!==null){let e=n.current,i=r.current,o=t.context.triggerElements.getById(e);i&&o===i&&(t.context.triggerElements.delete(e),a=!0),n.current=null,r.current=null}if(i!==null&&(n.current=e,r.current=i,t.context.triggerElements.add(e,i),a=!0),a){let e=t.context.triggerElements.size;t.select(`open`)&&t.state.triggerCount!==e&&t.set(`triggerCount`,e)}},[t,e])}function dl(e,t,n,r=!1){t?e.preventUnmountingOnClose=!1:r&&(e.preventUnmountingOnClose=!0);let i=n?.id??null;(i||t)&&(e.activeTriggerId=i,e.activeTriggerElement=n??null)}function fl(e){let t=!1;return e.preventUnmountOnClose=()=>{t=!0},()=>t}function pl(e,t,n,r={}){let i=n.reason,a=i===Ka,o=t&&i===`trigger-focus`,s=!t&&(i===`trigger-press`||i===`escape-key`),c=fl(n);if(e.context.onOpenChange?.(t,n),n.isCanceled)return;r.onBeforeDispatch?.(),e.state.floatingRootContext.dispatchOpenChange(t,n);let l=()=>{let i={...r.extraState,open:t};o?i.instantType=`focus`:s?i.instantType=`dismiss`:a&&(i.instantType=void 0),dl(i,t,n.trigger,c()),e.update(i)};a?Pa.flushSync(l):l()}function ml(e,t,n,r){let i=n.useState(`isMountedByTrigger`,e),a=ul(e,n),o=K(t=>{let i=n.select(`open`),a=n.select(`activeTriggerId`);if(a===e){n.update({activeTriggerElement:t,...i?r:null});return}a==null&&i&&n.update({activeTriggerId:e,activeTriggerElement:t,...r})}),s=_.useCallback(e=>{a(e),e&&o(e)},[a,o]);return q(()=>{i&&n.update({activeTriggerElement:t.current,...r})},[i,n,t,...Object.values(r)]),{registerTrigger:s,isMountedByThisTrigger:i}}function hl(e,t={}){let{closeOnActiveTriggerUnmount:n=!1}=t,r=_.useRef(null),i=e.useState(`open`);q(()=>{if(!i){r.current=null,e.state.triggerCount!==0&&e.set(`triggerCount`,0);return}let t=e.context.triggerElements.size,a={};e.state.triggerCount!==t&&(a.triggerCount=t);let o=e.select(`activeTriggerId`),s=null;if(o){let t=e.context.triggerElements.getById(o);if(t)r.current=o,t!==e.state.activeTriggerElement&&(a.activeTriggerElement=t);else{for(let[t,n]of e.context.triggerElements.entries())if(n===e.state.activeTriggerElement){a.activeTriggerId=t,a.activeTriggerElement=n,r.current=t;break}a.activeTriggerId===void 0&&(r.current===o?s=o:r.current=null)}}else r.current=null;if(!s&&!o&&t===1){let t=e.context.triggerElements.entries().next();if(!t.done){let[e,n]=t.value;a.activeTriggerId=e,a.activeTriggerElement=n,r.current=e}}(a.triggerCount!==void 0||a.activeTriggerId!==void 0||a.activeTriggerElement!==void 0)&&e.update(a),s&&n&&queueMicrotask(()=>{if(e.select(`open`)&&e.select(`activeTriggerId`)===s&&!e.context.triggerElements.getById(s)){let t=$(Wa);e.setOpen(!1,t),t.isCanceled||e.update({activeTriggerId:null,activeTriggerElement:null})}})},[i,e,e.useState(`triggerCount`),e.useState(`activeTriggerId`),e.useState(`activeTriggerElement`),n])}function gl(e,t,n){let{mounted:r,setMounted:i,transitionStatus:a}=Va(e),o=t.useState(`preventUnmountingOnClose`),s=!e&&o;t.useSyncedValues({mounted:r,transitionStatus:a,preventUnmountingOnClose:s});let c=K(()=>{i(!1),t.update({activeTriggerId:null,activeTriggerElement:null,mounted:!1,preventUnmountingOnClose:!1}),n?.(),t.context.onOpenChangeComplete?.(!1)});return Ia({enabled:r&&!e&&!s,open:e,ref:t.context.popupRef,onComplete(){e||c()}}),{forceUnmount:c,transitionStatus:a}}function _l(e,t){e.useSyncedValues(t),q(()=>()=>{e.update({activeTriggerProps:at,inactiveTriggerProps:at,popupProps:at})},[e])}function vl(e,t){q(()=>{!t&&e.state.openMethod!==null&&e.set(`openMethod`,null)},[t,e]),q(()=>()=>{e.state.openMethod!==null&&e.set(`openMethod`,null)},[e])}var yl=class{constructor(){this.idMap=new Map}add(e,t){this.idMap.set(e,t)}delete(e){this.idMap.delete(e)}hasElement(e){for(let t of this.idMap.values())if(t===e)return!0;return!1}hasMatchingElement(e){for(let t of this.idMap.values())if(e(t))return!0;return!1}getById(e){return this.idMap.get(e)}entries(){return this.idMap.entries()}elements(){return this.idMap.values()}get size(){return this.idMap.size}};function bl(){return new il({open:!1,transitionStatus:void 0,floatingElement:null,referenceElement:null,triggerElements:new yl,floatingId:void 0,syncOnly:!1,nested:!1,onOpenChange:void 0})}function xl(){return{open:!1,openProp:void 0,mounted:!1,transitionStatus:void 0,floatingRootContext:bl(),floatingId:void 0,triggerCount:0,preventUnmountingOnClose:!1,payload:void 0,activeTriggerId:null,activeTriggerElement:null,triggerIdProp:void 0,popupElement:null,positionerElement:null,activeTriggerProps:at,inactiveTriggerProps:at,popupProps:at}}function Sl(e,t,n=!1){return new il({open:!1,transitionStatus:void 0,floatingElement:null,referenceElement:null,triggerElements:e,floatingId:t,syncOnly:!0,nested:n,onOpenChange:void 0})}var Cl=e=>e.triggerIdProp??e.activeTriggerId,wl=e=>e.openProp??e.open,Tl=e=>(e.popupElement?.id??e.floatingId)||void 0;function El(e,t){return t!==void 0&&wl(e)&&Cl(e)===t}function Dl(e,t){return El(e,t)?!0:t!==void 0&&wl(e)&&Cl(e)==null&&e.triggerCount===1}var Ol={open:wl,mounted:e=>e.mounted,transitionStatus:e=>e.transitionStatus,floatingRootContext:e=>e.floatingRootContext,triggerCount:e=>e.triggerCount,preventUnmountingOnClose:e=>e.preventUnmountingOnClose,payload:e=>e.payload,activeTriggerId:Cl,activeTriggerElement:e=>e.mounted?e.activeTriggerElement:null,popupId:Tl,isTriggerActive:(e,t)=>t!==void 0&&Cl(e)===t,isOpenedByTrigger:(e,t)=>El(e,t),isMountedByTrigger:(e,t)=>t!==void 0&&Cl(e)===t&&e.mounted,triggerProps:(e,t)=>t?e.activeTriggerProps:e.inactiveTriggerProps,triggerPopupId:(e,t)=>Dl(e,t)?Tl(e):void 0,popupProps:e=>e.popupProps,popupElement:e=>e.popupElement,positionerElement:e=>e.positionerElement};function kl(e){let t=_.useCallback(t=>e===void 0?rt:e.subscribeStore(t),[e]),n=_.useCallback(()=>e===void 0?void 0:e.store,[e]);return(0,Jc.useSyncExternalStore)(t,n,()=>e?.serverStore)}function Al(e){let{open:t=!1,onOpenChange:n,elements:r={}}=e,i=Or(),a=bs()!=null,o=_e(()=>new il({open:t,transitionStatus:void 0,onOpenChange:n,referenceElement:r.reference??null,floatingElement:r.floating??null,triggerElements:new yl,floatingId:i,syncOnly:!1,nested:a})).current;return q(()=>{let e={open:t,floatingId:i};r.reference!==void 0&&(e.referenceElement=r.reference,e.domReferenceElement=V(r.reference)?r.reference:null),r.floating!==void 0&&(e.floatingElement=r.floating),o.update(e)},[t,i,r.reference,r.floating,o]),o.context.onOpenChange=n,o.context.nested=a,o}function jl(e){return Ml(e,e.rootContext)}function Ml(e,t){let{nodeId:n,externalTree:r}=e,i=t.useState(`referenceElement`),a=t.useState(`floatingElement`),o=t.useState(`domReferenceElement`),s=t.useState(`open`),c=t.useState(`floatingId`),[l,u]=_.useState(null),[d,f]=_.useState(void 0),[p,m]=_.useState(void 0),h=_.useRef(null),g=xs(r),v=_.useMemo(()=>({reference:i,floating:a,domReference:o}),[i,a,o]),y=Rc({...e,elements:{...v,...l&&{reference:l}}}),b=V(d)?d:null,x=p===void 0?t.state.floatingElement:p;t.useSyncedValue(`referenceElement`,d??null),t.useSyncedValue(`domReferenceElement`,d===void 0?o:b),t.useSyncedValue(`floatingElement`,x);let S=_.useCallback(e=>{let t=V(e)?{getBoundingClientRect:()=>e.getBoundingClientRect(),getClientRects:()=>e.getClientRects(),contextElement:e}:e;u(t),y.refs.setReference(t)},[y.refs]),C=_.useCallback(e=>{(V(e)||e===null)&&(h.current=e,f(e)),(V(y.refs.reference.current)||y.refs.reference.current===null||e!==null&&!V(e))&&y.refs.setReference(e)},[y.refs,f]),w=_.useCallback(e=>{m(e),y.refs.setFloating(e)},[y.refs]),T=_.useMemo(()=>({...y.refs,setReference:C,setFloating:w,setPositionReference:S,domReference:h}),[y.refs,C,w,S]),E=_.useMemo(()=>({...y.elements,domReference:o}),[y.elements,o]),D=_.useMemo(()=>({...y,dataRef:t.context.dataRef,open:s,onOpenChange:t.setOpen,events:t.context.events,floatingId:c,refs:T,elements:E,nodeId:n,rootStore:t}),[y,T,E,n,t,s,c]);return q(()=>{o&&(h.current=o)},[o]),q(()=>{t.context.dataRef.current.floatingContext=D;let e=g?.nodesRef.current.find(e=>e.id===n);e&&(e.context=D)}),_.useMemo(()=>({...y,context:D,refs:T,elements:E,rootStore:t}),[y,T,E,D,t])}var Nl=Gr&&qr;function Pl(e,t={}){let{enabled:n=!0,delay:r}=t,i=`rootStore`in e?e.rootStore:e,{events:a,dataRef:o}=i.context,s=_.useRef(!1),c=_.useRef(null),l=_.useRef(!0),u=Oa();_.useEffect(()=>{let e=i.select(`domReferenceElement`);if(!n)return;let t=R(e);function r(){let e=i.select(`domReferenceElement`);!i.select(`open`)&&H(e)&&e===ni(Ue(e))&&(s.current=!0)}function a(){l.current=!0}function o(){l.current=!1}return Ro(Lo(t,`blur`,r),Nl&&Lo(t,`keydown`,a,!0),Nl&&Lo(t,`pointerdown`,o,!0))},[i,n]),_.useEffect(()=>{if(!n)return;function e(e){if(e.reason===`trigger-press`||e.reason===`escape-key`){let e=i.select(`domReferenceElement`);V(e)&&(c.current=e,s.current=!0)}}return a.on(`openchange`,e),()=>{a.off(`openchange`,e)}},[a,n,i]);let d=_.useMemo(()=>{function e(){s.current=!1,c.current=null}return{onMouseLeave(){e()},onFocus(t){let n=t.currentTarget;if(s.current){if(c.current===n)return;e()}let a=ri(t.nativeEvent);if(V(a)){if(Nl&&!t.relatedTarget){if(!l.current&&!si(a))return}else if(!ui(a))return}let o=ii(t.relatedTarget,i.context.triggerElements),{nativeEvent:d,currentTarget:f}=t,p=typeof r==`function`?r():r;if(i.select(`open`)&&o||p===0||p===void 0){i.setOpen(!0,$(qa,d,f));return}u.start(p,()=>{s.current||i.setOpen(!0,$(qa,d,f))})},onBlur(t){e();let n=t.relatedTarget,r=t.nativeEvent,a=V(n)&&n.hasAttribute(Go(`focus-guard`))&&n.getAttribute(`data-type`)===`outside`;u.start(0,()=>{let e=i.select(`domReferenceElement`),t=ni(Ue(e));!n&&t===e||Q(o.current.floatingContext?.refs.floating.current,t)||Q(e,t)||a||ii(n??t,i.context.triggerElements)||i.setOpen(!1,$(qa,r))})}}},[o,r,i,u]);return _.useMemo(()=>n?{reference:d,trigger:d}:{},[n,d])}var Fl=class e{constructor(){this.pointerType=void 0,this.interactedInside=!1,this.handler=void 0,this.blockMouseMove=!0,this.performedPointerEventsMutation=!1,this.pointerEventsScopeElement=null,this.pointerEventsReferenceElement=null,this.pointerEventsFloatingElement=null,this.restTimeoutPending=!1,this.openChangeTimeout=new Da,this.restTimeout=new Da,this.handleCloseOptions=void 0}static create(){return new e}dispose=()=>{this.openChangeTimeout.clear(),this.restTimeout.clear()};disposeEffect=()=>this.dispose},Il=new WeakMap;function Ll(e){if(!e.performedPointerEventsMutation)return;let t=e.pointerEventsScopeElement;t&&Il.get(t)===e&&(e.pointerEventsScopeElement?.style.removeProperty(`pointer-events`),e.pointerEventsReferenceElement?.style.removeProperty(`pointer-events`),e.pointerEventsFloatingElement?.style.removeProperty(`pointer-events`),Il.delete(t)),e.performedPointerEventsMutation=!1,e.pointerEventsScopeElement=null,e.pointerEventsReferenceElement=null,e.pointerEventsFloatingElement=null}function Rl(e,t){let{scopeElement:n,referenceElement:r,floatingElement:i}=t,a=Il.get(n);a&&a!==e&&Ll(a),Ll(e),e.performedPointerEventsMutation=!0,e.pointerEventsScopeElement=n,e.pointerEventsReferenceElement=r,e.pointerEventsFloatingElement=i,Il.set(n,e),n.style.pointerEvents=`none`,r.style.pointerEvents=`auto`,i.style.pointerEvents=`auto`}function zl(e){let t=e.context.dataRef.current,n=_e(()=>t.hoverInteractionState??Fl.create()).current;return t.hoverInteractionState||=n,Ta(t.hoverInteractionState.disposeEffect),t.hoverInteractionState}function Bl(e,t={}){let{enabled:n=!0,closeDelay:r=0,nodeId:i}=t,a=`rootStore`in e?e.rootStore:e,o=a.useState(`open`),s=a.useState(`floatingElement`),c=a.useState(`domReferenceElement`),{dataRef:l}=a.context,u=xs(),d=bs(),f=zl(a),p=Oa(),m=K(()=>jo(l.current.openEvent?.type,f.interactedInside)),h=K(()=>Mo(l.current.openEvent?.type)),g=K(()=>{Ll(f)});q(()=>{o||(f.pointerType=void 0,f.restTimeoutPending=!1,f.interactedInside=!1,g())},[o,f,g]),_.useEffect(()=>g,[g]),q(()=>{if(n&&o&&f.handleCloseOptions?.blockPointerEvents&&h()&&V(c)&&s){let e=c,t=s,n=Ue(s),r=u?.nodesRef.current.find(e=>e.id===d)?.context?.elements.floating;r&&(r.style.pointerEvents=``);let i=f.pointerEventsScopeElement===t?null:f.pointerEventsScopeElement,a=r===t?null:r,o=f.handleCloseOptions?.getScope?.()??i??a??e.closest(`[data-rootownerid]`)??n.body;return Rl(f,{scopeElement:o,referenceElement:e,floatingElement:t}),()=>{g()}}},[n,o,c,s,f,h,u,d,g]),_.useEffect(()=>{if(!n)return;function e(){return!!(u&&d&&fi(u.nodesRef.current,d).length>0)}function t(e){let t=ko(r,`close`,f.pointerType),n=()=>{a.setOpen(!1,$(Ka,e)),u?.events.emit(`floating.closed`,e)};t?f.openChangeTimeout.start(t,n):(f.openChangeTimeout.clear(),n())}function o(e){let t=ri(e);if(!ci(t)){f.interactedInside=!1;return}f.interactedInside=t?.closest(`[aria-haspopup]`)!=null}function c(){f.openChangeTimeout.clear(),p.clear(),u?.events.off(`floating.closed`,v),g()}function _(n){if(e()&&u){u.events.on(`floating.closed`,v);return}if(ii(n.relatedTarget,a.context.triggerElements))return;let r=l.current.floatingContext?.nodeId??i,o=n.relatedTarget;if(!(u&&r&&V(o)&&fi(u.nodesRef.current,r,!1).some(e=>Q(e.context?.elements.floating,o)))){if(f.handler){f.handler(n);return}g(),h()&&!m()&&t(n)}}function v(t){!u||!d||e()||p.start(0,()=>{u.events.off(`floating.closed`,v),a.setOpen(!1,$(Ka,t)),u.events.emit(`floating.closed`,t)})}let y=s;return Ro(y&&Lo(y,`mouseenter`,c),y&&Lo(y,`mouseleave`,_),y&&Lo(y,`pointerdown`,o,!0),()=>{u?.events.off(`floating.closed`,v)})},[n,s,a,l,r,i,h,m,g,f,u,d,p])}var Vl={current:null};function Hl(e,t={}){let{enabled:n=!0,delay:r=0,handleClose:i=null,mouseOnly:a=!1,restMs:o=0,move:s=!0,triggerElementRef:c=Vl,externalTree:l,isActiveTrigger:u=!0,getHandleCloseContext:d,isClosing:f,shouldOpen:p,guardStaleOpen:m=!1}=t,h=`rootStore`in e?e.rootStore:e,{dataRef:g,events:v}=h.context,y=xs(l),b=zl(h),x=_.useRef(!1),S=zo(i),C=zo(r),w=zo(o),T=zo(n),E=zo(p),D=zo(f),O=K(()=>jo(g.current.openEvent?.type,b.interactedInside)),k=K(()=>E.current?.()!==!1),A=K((e,t,n)=>{let r=h.context.triggerElements;if(r.hasElement(t))return!e||!Q(e,t);if(!V(n))return!1;let i=n;return r.hasMatchingElement(e=>Q(e,i))&&(!e||!Q(e,i))}),j=K(()=>{b.handler&&=(Ue(h.select(`domReferenceElement`)).removeEventListener(`mousemove`,b.handler),void 0)}),M=K(()=>{Ll(b)});return u&&(b.handleCloseOptions=S.current?.__options),_.useEffect(()=>j,[j]),_.useEffect(()=>{if(!n)return;function e(e){e.open?x.current=!1:(x.current=e.reason===Ka,j(),b.openChangeTimeout.clear(),b.restTimeout.clear(),b.blockMouseMove=!0,b.restTimeoutPending=!1)}return v.on(`openchange`,e),()=>{v.off(`openchange`,e)}},[n,v,b,j]),_.useEffect(()=>{if(!n)return;function e(e,t=!0){let n=ko(C.current,`close`,b.pointerType);n?b.openChangeTimeout.start(n,()=>{h.setOpen(!1,$(Ka,e)),y?.events.emit(`floating.closed`,e)}):t&&(b.openChangeTimeout.clear(),h.setOpen(!1,$(Ka,e)),y?.events.emit(`floating.closed`,e))}let t=c.current??(u?h.select(`domReferenceElement`):null);if(!V(t))return;function r(e){if(b.openChangeTimeout.clear(),b.blockMouseMove=!1,a&&!vi(b.pointerType))return;let t=Ao(w.current),n=ko(C.current,`open`,b.pointerType),r=ri(e),i=e.currentTarget??null,o=h.select(`domReferenceElement`),s=i;if(V(r)&&!h.context.triggerElements.hasElement(r)){for(let e of h.context.triggerElements.elements())if(Q(e,r)){s=e;break}}V(i)&&V(o)&&!h.context.triggerElements.hasElement(i)&&Q(i,o)&&(s=o);let c=s!=null&&A(o,s,r),l=h.select(`open`),u=D.current?.()??h.select(`transitionStatus`)===`ending`,d=!l&&u&&x.current,f=!c&&V(s)&&V(o)&&Q(o,s)&&d,p=t>0&&!n,m=c&&(l||d)||f,g=!l||c;if(m){k()&&h.setOpen(!0,$(Ka,e,s));return}p||(n?b.openChangeTimeout.start(n,()=>{g&&k()&&h.setOpen(!0,$(Ka,e,s))}):g&&k()&&h.setOpen(!0,$(Ka,e,s)))}function i(t){if(O()){M();return}j();let n=Ue(h.select(`domReferenceElement`));b.restTimeout.clear(),b.restTimeoutPending=!1;let r=g.current.floatingContext??d?.();if(!ii(t.relatedTarget,h.context.triggerElements)){if(S.current&&r){h.select(`open`)||b.openChangeTimeout.clear();let i=c.current;b.handler=S.current({...r,tree:y,x:t.clientX,y:t.clientY,onClose(){M(),j(),T.current&&!O()&&i===h.select(`domReferenceElement`)&&e(t,!0)}}),n.addEventListener(`mousemove`,b.handler),b.handler(t);return}(b.pointerType!==`touch`||!Q(h.select(`floatingElement`),t.relatedTarget))&&e(t)}}function o(e){Q(t,e.relatedTarget)||(b.openChangeTimeout.clear(),b.restTimeout.clear(),b.restTimeoutPending=!1)}let l=m?Lo(t,`mouseout`,o):void 0;return s?Ro(Lo(t,`mousemove`,r,{once:!0}),Lo(t,`mouseenter`,r),Lo(t,`mouseleave`,i),l):Ro(Lo(t,`mouseenter`,r),Lo(t,`mouseleave`,i),l)},[j,M,g,C,h,n,S,b,u,A,O,a,s,w,c,y,T,d,D,k,m]),_.useMemo(()=>{if(!n)return;function e(e){b.pointerType=e.pointerType}return{onPointerDown:e,onPointerEnter:e,onMouseMove(e){let{nativeEvent:t}=e,n=e.currentTarget,r=h.select(`domReferenceElement`),i=h.select(`open`),o=A(r,n,e.target);if(a&&!vi(b.pointerType))return;if(i&&o&&b.handleCloseOptions?.blockPointerEvents){let e=h.select(`floatingElement`);if(e){let t=b.handleCloseOptions?.getScope?.()??n.ownerDocument.body;Rl(b,{scopeElement:t,referenceElement:n,floatingElement:e})}}let s=Ao(w.current);if(i&&!o||s===0||!o&&b.restTimeoutPending&&e.movementX**2+e.movementY**2<2)return;b.restTimeout.clear();function c(){if(b.restTimeoutPending=!1,O())return;let e=h.select(`open`);!b.blockMouseMove&&(!e||o)&&k()&&h.setOpen(!0,$(Ka,t,n))}b.pointerType===`touch`?Pa.flushSync(()=>{c()}):o&&i?c():(b.restTimeoutPending=!0,b.restTimeout.start(s,c))}}},[n,b,O,A,a,h,w,k])}var Ul=`Escape`;function Wl(e){return qr&&e.movementX===0&&e.movementY===0}function Gl(e,t,n){switch(e){case`vertical`:return t;case`horizontal`:return n;default:return t||n}}function Kl(e,t){return Gl(t,e===`ArrowUp`||e===`ArrowDown`,e===`ArrowLeft`||e===`ArrowRight`)}function ql(e,t,n){return Gl(t,e===`ArrowDown`,n?e===`ArrowLeft`:e===`ArrowRight`)||e===`Enter`||e===` `||e===``}function Jl(e,t,n){return Gl(t,n?e===Qr:e===$r,e===ti)}function Yl(e,t,n,r){return t===`both`||t===`horizontal`&&r?e===Ul:Gl(t,n?e===$r:e===Qr,e===ei)}function Xl(e,t){let{listRef:n,activeIndex:r,onNavigate:i=()=>{},enabled:a=!0,selectedIndex:o=null,allowEscape:s=!1,loopFocus:c=!1,nested:l=!1,rtl:u=!1,virtual:d=!1,focusItemOnOpen:f=`auto`,focusItemOnHover:p=!0,openOnArrowKeyDown:m=!0,disabledIndices:h=void 0,orientation:g=`vertical`,parentOrientation:v,id:y,resetOnPointerLeave:b=!0,externalTree:x,grid:S}=t,C=S!=null,w=`rootStore`in e?e.rootStore:e,T=w.useState(`open`),E=w.useState(`floatingElement`),D=w.useState(`domReferenceElement`),O=w.context.dataRef,k=di(E),A=li(D),j=zo(k),M=bs(),N=xs(x),P=_.useRef(f),F=_.useRef(o??-1),I=_.useRef(null),L=_.useRef(!0),R=K(e=>{i(F.current===-1?null:F.current,e)}),z=_.useRef(!!E),B=_.useRef(T),V=_.useRef(!1),U=_.useRef(!1),W=_.useRef(null),ee=zo(h),te=zo(T),G=zo(o),ne=zo(b),re=Ma(),ie=Ma(),ae=K(()=>{function e(e){d?N?.events.emit(`virtualfocus`,e):W.current=qo(e,{sync:V.current,preventScroll:!0})}let t=n.current[F.current],r=U.current;t&&e(t),(V.current?e=>e():e=>re.request(e))(()=>{let i=n.current[F.current]||t;i&&(t||e(i),de&&(r||!L.current)&&i.scrollIntoView?.({block:`nearest`,inline:`nearest`}))})});q(()=>{O.current.orientation=g},[O,g]),q(()=>{a&&(T&&E?(F.current=o??-1,P.current&&o!=null&&(U.current=!0,R())):z.current&&(F.current=-1,R()))},[a,T,E,o,R]),q(()=>{if(a){if(!T){V.current=!1;return}if(E){if(r==null){if(V.current=!1,G.current!=null)return;if(z.current&&(F.current=-1,ae()),(!B.current||!z.current)&&P.current&&(I.current!=null||P.current===!0&&I.current==null)){let e=0,t=()=>{n.current[0]==null?(e<2&&(e?e=>ie.request(e):queueMicrotask)(t),e+=1):(F.current=I.current==null||ql(I.current,g,u)||l?Ji(n):Yi(n),I.current=null,R())};t()}}else qi(n.current,r)||(F.current=r,ae(),U.current=!1)}}},[a,T,E,r,G,l,n,g,u,R,ae,ie]),q(()=>{if(!a||E||!N||d||!z.current)return;let e=N.nodesRef.current,t=e.find(e=>e.id===M)?.context?.elements.floating,n=ni(Ue(D??t??null)),r=e.some(e=>e.context&&Q(e.context.elements.floating,n));t&&!r&&L.current&&t.focus({preventScroll:!0})},[a,E,D,N,M,d]),q(()=>{B.current=T,z.current=!!E}),q(()=>{T||(I.current=null,P.current=f)},[T,f]);let oe=r!=null,se=K(e=>{if(!te.current)return;let t=n.current.indexOf(e.currentTarget);t!==-1&&(F.current!==t||r!==t)&&(F.current=t,R(e))}),ce=K(()=>v??N?.nodesRef.current.find(e=>e.id===M)?.context?.dataRef?.current.orientation),le=K(()=>Ji(n,ee.current)),ue=K(e=>{if(L.current=!1,V.current=!0,e.which===229||!te.current&&e.currentTarget===j.current)return;if(l&&Yl(e.key,g,u,C)){Kl(e.key,ce())||mi(e),w.setOpen(!1,$(to,e.nativeEvent)),H(D)&&(d?N?.events.emit(`virtualfocus`,D):D.focus());return}let t=F.current,r=Ji(n,h),i=Yi(n,h);if(A||(e.key===`Home`&&(mi(e),F.current=r,R(e)),e.key===`End`&&(mi(e),F.current=i,R(e))),S!=null){let t=S(e,F.current,n,g,c,u,h,r,i);if(t!=null&&(F.current=t,R(e)),g===`both`)return}if(Kl(e.key,g)){if(mi(e),T&&!d&&ni(e.currentTarget.ownerDocument)===e.currentTarget){F.current=ql(e.key,g,u)?r:i,R(e);return}ql(e.key,g,u)?c?t>=i?s&&t!==n.current.length?F.current=-1:(V.current=!1,F.current=r):F.current=Xi(n.current,{startingIndex:t,disabledIndices:h}):F.current=Math.min(i,Xi(n.current,{startingIndex:t,disabledIndices:h})):c?t<=r?s&&t!==-1?F.current=n.current.length:(V.current=!1,F.current=i):F.current=Xi(n.current,{startingIndex:t,decrement:!0,disabledIndices:h}):F.current=Math.max(r,Xi(n.current,{startingIndex:t,decrement:!0,disabledIndices:h})),qi(n.current,F.current)&&(F.current=-1),R(e)}}),de=_.useMemo(()=>({onFocus(e){V.current=!0,se(e)},onClick:({currentTarget:e})=>e.focus({preventScroll:!0}),onMouseMove(e){Wl(e)||(V.current=!0,U.current=!1,p&&se(e))},onPointerLeave(e){if(!te.current||!L.current||e.pointerType===`touch`)return;V.current=!0;let t=e.relatedTarget;if(!(!p||n.current.includes(t))&&ne.current&&(W.current?.(),W.current=null,F.current=-1,R(e),!d)){let e=j.current,t=ni(Ue(e));e&&Q(e,t)&&e.focus({preventScroll:!0})}}}),[se,te,j,p,n,R,ne,d]),fe=_.useMemo(()=>d&&T&&oe&&{"aria-activedescendant":`${y}-${r}`},[d,T,oe,y,r]),pe=_.useMemo(()=>({"aria-orientation":g===`both`?void 0:g,...A?{}:fe,onKeyDown(e){if(e.key===`Tab`&&e.shiftKey&&T&&!d){let t=ri(e.nativeEvent);if(t&&!Q(j.current,t))return;mi(e),w.setOpen(!1,$($a,e.nativeEvent)),H(D)&&D.focus();return}ue(e)},onPointerMove(e){Wl(e)||(L.current=!0)}}),[fe,ue,j,g,A,w,T,d,D]),me=_.useMemo(()=>{function e(e){w.setOpen(!0,$(to,e.nativeEvent,e.currentTarget))}function t(e){f===`auto`&&gi(e.nativeEvent)&&(P.current=!d)}function n(e){P.current=f,f===`auto`&&_i(e.nativeEvent)&&(P.current=!0)}return{onKeyDown(t){let n=w.select(`open`);L.current=!1;let r=t.key.startsWith(`Arrow`),i=Jl(t.key,ce(),u),a=Kl(t.key,g),o=(l?i:a)||t.key===`Enter`||t.key.trim()===``;if(d&&n)return ue(t);if(!(!n&&!m&&r)){if(o){let e=Kl(t.key,ce());I.current=l&&e?null:t.key}if(l){i&&(mi(t),n?(F.current=le(),R(t)):e(t));return}a&&(G.current!=null&&(F.current=G.current),mi(t),!n&&m?e(t):ue(t),n&&R(t))}},onFocus(e){w.select(`open`)&&!d&&(F.current=-1,R(e))},onPointerDown:n,onPointerEnter:n,onMouseDown:t,onClick:t}},[ue,f,le,l,R,w,m,g,ce,u,G,d]),he=_.useMemo(()=>({...fe,...me}),[fe,me]);return _.useMemo(()=>a?{reference:he,floating:pe,item:de,trigger:me}:{},[a,he,pe,me,de])}function Zl(e,t){let{listRef:n,elementsRef:r,activeIndex:i,onMatch:a,disabledIndices:o,onTyping:s,enabled:c=!0,resetMs:l=750,selectedIndex:u=null}=t,d=`rootStore`in e?e.rootStore:e,f=d.useState(`open`),p=Oa(),m=_.useRef(``),h=_.useRef(u??i??-1),g=_.useRef(null),v=K(e=>{function t(e){return r?.current[e]}function c(e){let n=t(e);return n&&!$i(n)||n?.matches(`:disabled`)?!1:o==null||!Zi(it,e,o)}function d(e,t,n=0){if(e.length===0)return-1;let r=(n%e.length+e.length)%e.length,i=t.toLowerCase();for(let t=0;t<e.length;t+=1){let n=(r+t)%e.length;if(!(!e[n]?.toLowerCase().startsWith(i)||!c(n)))return n}return-1}let _=n.current;if(m.current.length>0&&e.key===` `&&(mi(e),s?.(!0)),m.current.length>0&&m.current[0]!==` `&&d(_,m.current)===-1&&e.key!==` `&&s?.(!1),_==null||e.key.length!==1||e.ctrlKey||e.metaKey||e.altKey)return;f&&e.key!==` `&&(mi(e),s?.(!0));let v=m.current===``;v&&(h.current=u??i??-1),_.every((e,t)=>e&&c(t)?e[0]?.toLowerCase()!==e[1]?.toLowerCase():!0)&&m.current===e.key&&(m.current=``,h.current=g.current),m.current+=e.key,p.start(l,()=>{m.current=``,h.current=g.current,s?.(!1)});let y=((v?u??i??-1:h.current)??0)+1,b=d(_,m.current,y);b===-1?e.key!==` `&&(m.current=``,s?.(!1)):(a?.(b),g.current=b)}),y=K(e=>{let t=e.relatedTarget,n=d.select(`domReferenceElement`),r=d.select(`floatingElement`);Q(n,t)||Q(r,t)||(p.clear(),m.current=``,h.current=g.current,s?.(!1))});q(()=>{!f&&u!==null||(p.clear(),g.current=null,m.current!==``&&(m.current=``))},[f,u,p]);let b=_.useMemo(()=>({onKeyDown:v,onBlur:y}),[v,y]);return _.useMemo(()=>c?{reference:b,floating:b}:{},[c,b])}var Ql=.1,$l=Ql*Ql,eu=.5;function tu(e,t,n,r,i,a){return r>=t!=a>=t&&e<=(i-n)*(t-r)/(a-r)+n}function nu(e,t,n,r,i,a,o,s,c,l){let u=!1;return tu(e,t,n,r,i,a)&&(u=!u),tu(e,t,i,a,o,s)&&(u=!u),tu(e,t,o,s,c,l)&&(u=!u),tu(e,t,c,l,n,r)&&(u=!u),u}function ru(e,t,n){return e>=n.x&&e<=n.x+n.width&&t>=n.y&&t<=n.y+n.height}function iu(e,t,n,r,i,a){return e>=Math.min(n,i)&&e<=Math.max(n,i)&&t>=Math.min(r,a)&&t<=Math.max(r,a)}function au(e={}){let{blockPointerEvents:t=!1}=e,n=new Da,r=({x:e,y:t,placement:r,elements:i,onClose:a,nodeId:o,tree:s})=>{let c=r?.split(`-`)[0],l=!1,u=null,d=null,f=typeof performance<`u`?performance.now():0;function p(e,t){let n=performance.now(),r=n-f;if(u===null||d===null||r===0)return u=e,d=t,f=n,!1;let i=e-u,a=t-d,o=i*i+a*a,s=r*r*$l;return u=e,d=t,f=n,o<s}function m(){n.clear(),a()}return function(r){n.clear();let a=i.domReference,u=i.floating;if(!a||!u||c==null||e==null||t==null)return;let{clientX:d,clientY:f}=r,h=ri(r),g=r.type===`mouseleave`,_=Q(u,h),v=Q(a,h);if(_&&(l=!0,!g))return;if(v&&(l=!1,!g)){l=!0;return}if(g&&V(r.relatedTarget)&&Q(u,r.relatedTarget))return;function y(){return!!(s&&fi(s.nodesRef.current,o).length>0)}function b(){y()||m()}if(y())return;let x=a.getBoundingClientRect(),S=u.getBoundingClientRect(),C=e>S.right-S.width/2,w=t>S.bottom-S.height/2,T=S.width>x.width,E=S.height>x.height,D=(T?x:S).left,O=(T?x:S).right,k=(E?x:S).top,A=(E?x:S).bottom;if(c===`top`&&t>=x.bottom-1||c===`bottom`&&t<=x.top+1||c===`left`&&e>=x.right-1||c===`right`&&e<=x.left+1){b();return}let j=!1;switch(c){case`top`:j=iu(d,f,D,x.top+1,O,S.bottom-1);break;case`bottom`:j=iu(d,f,D,S.top+1,O,x.bottom-1);break;case`left`:j=iu(d,f,S.right-1,A,x.left+1,k);break;case`right`:j=iu(d,f,x.right-1,A,S.left+1,k)}if(j)return;if(l&&!ru(d,f,x)){b();return}if(!g&&p(d,f)){b();return}let M=!1;switch(c){case`top`:{let n=T?eu/2:eu*4,r=T||C?e+n:e-n,i=T?e-n:C?e+n:e-n,a=t+eu+1,o=C||T?S.bottom-eu:S.top,s=C?T?S.bottom-eu:S.top:S.bottom-eu;M=nu(d,f,r,a,i,a,S.left,o,S.right,s);break}case`bottom`:{let n=T?eu/2:eu*4,r=T||C?e+n:e-n,i=T?e-n:C?e+n:e-n,a=t-eu,o=C||T?S.top+eu:S.bottom,s=C?T?S.top+eu:S.bottom:S.top+eu;M=nu(d,f,r,a,i,a,S.left,o,S.right,s);break}case`left`:{let n=E?eu/2:eu*4,r=E||w?t+n:t-n,i=E?t-n:w?t+n:t-n,a=e+eu+1,o=w||E?S.right-eu:S.left,s=w?E?S.right-eu:S.left:S.right-eu;M=nu(d,f,o,S.top,s,S.bottom,a,r,a,i);break}case`right`:{let n=E?eu/2:eu*4,r=E||w?t+n:t-n,i=E?t-n:w?t+n:t-n,a=e-eu,o=w||E?S.left+eu:S.right,s=w?E?S.left+eu:S.right:S.left+eu;M=nu(d,f,a,r,a,i,o,S.top,s,S.bottom);break}}M?l||n.start(40,b):b()}};return r.__options={...e,blockPointerEvents:t},r}var ou={...Ol,disabled:e=>e.disabled,instantType:e=>e.instantType,isInstantPhase:e=>e.isInstantPhase,trackCursorAxis:e=>e.trackCursorAxis,disableHoverablePopup:e=>e.disableHoverablePopup,lastOpenChangeReason:e=>e.openChangeReason,closeOnClick:e=>e.closeOnClick,closeDelay:e=>e.closeDelay,adaptiveOrigin:e=>e.adaptiveOrigin},su=class extends nl{constructor(e,t,n){let r=new yl;super(cu(e,r,t,n),lu(r),ou)}setOpen=(e,t)=>{pl(this,e,t,{extraState:{openChangeReason:t.reason}})};cancelPendingOpen(e){this.state.floatingRootContext.dispatchOpenChange(!1,$(Ga,e))}};function cu(e,t,n,r=!1){let i={...xl(),disabled:!1,instantType:void 0,isInstantPhase:!1,trackCursorAxis:`none`,disableHoverablePopup:!1,openChangeReason:null,closeOnClick:!0,closeDelay:0,adaptiveOrigin:void 0,...e};return i.floatingRootContext=Sl(t,n,r),i}function lu(e){return{popupRef:_.createRef(),onOpenChange:void 0,onOpenChangeComplete:void 0,triggerElements:e}}var uu=Co(function(e){let{disabled:t=!1,defaultOpen:n=!1,open:r,disableHoverablePopup:i=!1,trackCursorAxis:a=`none`,actionsRef:o,onOpenChange:s,onOpenChangeComplete:c,handle:l,triggerId:u,defaultTriggerId:d=null,children:f}=e,p=cl((e,t)=>new su({open:n,openProp:r,activeTriggerId:d,triggerIdProp:u},e,t));p.useControlledProp(`openProp`,r),p.useControlledProp(`triggerIdProp`,u),p.useContextCallback(`onOpenChange`,s),p.useContextCallback(`onOpenChangeComplete`,c);let m=p.useState(`open`),h=!t&&m,g=p.useState(`activeTriggerId`),v=p.useState(`mounted`),y=p.useState(`payload`);p.useSyncedValues({trackCursorAxis:a,disableHoverablePopup:i,disabled:t}),hl(p,{closeOnActiveTriggerUnmount:!0});let{forceUnmount:b,transitionStatus:x}=gl(h,p),S=p.useState(`isInstantPhase`),C=p.useState(`instantType`),w=p.useState(`lastOpenChangeReason`),T=_.useRef(null);q(()=>{m&&t&&p.setOpen(!1,$(ao))},[m,t,p]),q(()=>{x===`ending`&&w===`none`||x!==`ending`&&S?(C!==`delay`&&(T.current=C),p.set(`instantType`,`delay`)):T.current!==null&&(p.set(`instantType`,T.current),T.current=null)},[x,S,w,C,p]),q(()=>{h&&(g??p.set(`payload`,void 0))},[p,g,h]),_.useImperativeHandle(o,()=>({unmount:b,close:()=>p.setOpen(!1,$(co))}),[b,p]);let E=h||v||!t&&a!==`none`;return(0,Z.jsxs)(Eo.Provider,{value:p,children:[l&&(0,Z.jsx)(ll,{handle:l,store:p}),E&&(0,Z.jsx)(du,{store:p,disabled:t,trackCursorAxis:a}),typeof f==`function`?f({payload:y}):f]})});function du({store:e,disabled:t,trackCursorAxis:n}){let r=e.useState(`floatingRootContext`),i=Bs(r,{enabled:!t,referencePress:()=>e.select(`closeOnClick`)}),a=Ls(r,{enabled:!t&&n!==`none`,axis:n===`none`?void 0:n}),o=_.useMemo(()=>we(a.reference,i.reference),[a.reference,i.reference]);return _l(e,{activeTriggerProps:o,inactiveTriggerProps:o,popupProps:i.floating??at}),null}(function(e){return e.open=`data-open`,e.closed=`data-closed`,e[e.startingStyle=La.startingStyle]=`startingStyle`,e[e.endingStyle=La.endingStyle]=`endingStyle`,e.anchorHidden=`data-anchor-hidden`,e.side=`data-side`,e.align=`data-align`,e})({});var fu={"data-popup-open":``},pu={"data-popup-open":``,"data-pressed":``},mu={"data-open":``},hu={"data-closed":``},gu={"data-anchor-hidden":``},_u={open(e){return e?fu:null}},vu={open(e){return e?pu:null}},yu={open(e){return e?mu:hu},anchorHidden(e){return e?gu:null}},bu={...yu,...Ba},xu=_.createContext(void 0);function Su(){return _.useContext(xu)}var Cu=`data-base-ui-tooltip-trigger`;function wu(e){if(`composedPath`in e){let t=e.composedPath();for(let e=0;e<t.length;e+=1){let n=t[e];if(V(n))return n}}let t=e.target;return V(t)?t:null}function Tu(e){let t=e;for(;t;){let e=t.closest(`[${Cu}]`);if(e)return e;let n=t.getRootNode();t=`host`in n&&V(n.host)?n.host:null}return null}var Eu=wo(function(e,t){let{render:n,className:r,style:i,handle:a,payload:o,disabled:s,delay:c,closeOnClick:l=!0,closeDelay:u,id:d,...f}=e,p=Do(!0),m=kl(a)??p;if(!m)throw Error(ze(82));let h=kr(d),g=m.useState(`isTriggerActive`,h),v=m.useState(`isOpenedByTrigger`,h),y=m.useState(`floatingRootContext`),b=_.useRef(null),x=c??600,S=u??0,{registerTrigger:C,isMountedByThisTrigger:w}=ml(h,b,m,{payload:o,closeOnClick:l,closeDelay:S}),T=Su(),{delayRef:E,isInstantPhase:D,hasProvider:O}=Io(y,{open:v}),k=zl(y);m.useSyncedValue(`isInstantPhase`,D);let A=m.useState(`disabled`),j=s??A,M=zo(j),N=m.useState(`trackCursorAxis`),P=m.useState(`disableHoverablePopup`),F=_.useRef(!1),I=Oa(),L=_.useRef(void 0);function R(){return O?ko(E.current,`open`)===0?0:c??T??600:x}function z(e){let t=b.current;if(!t||!e)return!1;let n=Tu(e);return n!==null&&n!==t&&Q(t,n)}function B(e){let t=z(e);return F.current=t,t&&(k.openChangeTimeout.clear(),k.restTimeout.clear(),k.restTimeoutPending=!1,I.clear()),t}let V=Hl(y,{enabled:!j,mouseOnly:!0,move:!1,handleClose:!P&&N!==`both`?au():null,restMs:R,delay(){return u==null&&O?{close:ko(E.current,`close`)}:{close:S}},triggerElementRef:b,isActiveTrigger:g,isClosing:()=>m.select(`transitionStatus`)===`ending`,shouldOpen(){return!F.current}}),H=Pl(y,{enabled:!j}).reference,U=e=>{let t=F.current,n=wu(e),r=B(n),i=b.current,a=i&&n&&Q(i,n);if(r&&m.select(`open`)&&m.select(`lastOpenChangeReason`)===`trigger-hover`){m.setOpen(!1,$(Ka,e));return}if(t&&!r&&a&&!M.current&&!m.select(`open`)&&i&&vi(L.current)){let t=()=>{!F.current&&!M.current&&!m.select(`open`)&&m.setOpen(!0,$(Ka,e,i))},n=R();n===0?(I.clear(),t()):I.start(n,t)}},W=m.useState(`triggerProps`,w);return lt(`button`,e,{state:{open:v},ref:[t,C,b],props:[V,H,w||N!==`none`?W:void 0,{onMouseOver(e){U(e.nativeEvent)},onFocus(e){z(wu(e.nativeEvent))&&e.preventBaseUIHandler()},onMouseLeave(){F.current=!1,I.clear(),L.current=void 0},onPointerEnter(e){L.current=e.pointerType},onPointerDown(e){L.current=e.pointerType,m.set(`closeOnClick`,l),l&&!m.select(`open`)&&m.cancelPendingOpen(e.nativeEvent)},onClick(e){l&&!m.select(`open`)&&m.cancelPendingOpen(e.nativeEvent)},id:h,"data-trigger-disabled":j?``:void 0,[Cu]:j?void 0:``},f],stateAttributesMapping:_u})}),Du=_.createContext(void 0);function Ou(){let e=_.useContext(Du);if(e===void 0)throw Error(ze(70));return e}var ku=_.forwardRef(function(e,t){let{children:n,container:r,className:i,render:a,style:o,...s}=e,{node:c,subtree:l}=ms({container:r,ref:t,componentProps:e,elementProps:s});return!l&&!c?null:(0,Z.jsxs)(_.Fragment,{children:[l,c&&Pa.createPortal(n,c)]})}),Au=_.forwardRef(function(e,t){let{keepMounted:n=!1,...r}=e;return Do().useState(`mounted`)||n?(0,Z.jsx)(Du.Provider,{value:n,children:(0,Z.jsx)(ku,{ref:t,...r})}):null}),ju=_.createContext(void 0);function Mu(){let e=_.useContext(ju);if(e===void 0)throw Error(ze(71));return e}var Nu=_.createContext(void 0);function Pu(){return _.useContext(Nu)?.direction??`ltr`}var Fu=e=>({name:`arrow`,options:e,async fn(t){let{x:n,y:r,placement:i,rects:a,platform:o,elements:s,middlewareData:c}=t,{element:l,padding:u=0,offsetParent:d=`real`}=Di(e,t)||{};if(l==null)return{};let f=Gi(u),p={x:n,y:r},m=Ni(i),h=ji(m),g=await o.getDimensions(l),_=m===`y`,v=_?`top`:`left`,y=_?`bottom`:`right`,b=_?`clientHeight`:`clientWidth`,x=a.reference[h]+a.reference[m]-p[m]-a.floating[h],S=p[m]-a.reference[m],C=d===`real`?await o.getOffsetParent?.(l):s.floating,w=s.floating[b]||a.floating[h];(!w||!await o.isElement?.(C))&&(w=s.floating[b]||a.floating[h]);let T=x/2-S/2,E=w/2-g[h]/2-1,D=Math.min(f[v],E),O=Math.min(f[y],E),k=D,A=w-g[h]-O,j=w/2-g[h]/2+T,M=Ei(k,j,A),N=!c.arrow&&ki(i)!=null&&j!==M&&a.reference[h]/2-(j<k?D:O)-g[h]/2<0,P=N?j<k?j-k:j-A:0;return{[m]:p[m]+P,data:{[m]:M,centerOffset:j-M-P,...N&&{alignmentOffset:P}},reset:N}}}),Iu=(e,t)=>({...Fu(e),options:[e,t]}),Lu={name:`hide`,async fn(e){let{width:t,height:n,x:r,y:i}=e.rects.reference,a=t===0&&n===0&&r===0&&i===0,o=await e.platform.detectOverflow(e,{elementContext:`reference`});return{data:{referenceHidden:o.top-n>=0||o.right-t>=0||o.bottom-n>=0||o.left-t>=0||a}}}},Ru={sideX:`left`,sideY:`top`},zu=`--available-width`,Bu=`--available-height`;function Vu(e,t,n){let r=e===`inline-start`||e===`inline-end`;return{top:`top`,right:r?n?`inline-start`:`inline-end`:`right`,bottom:`bottom`,left:r?n?`inline-end`:`inline-start`:`left`}[t]}function Hu(e,t,n){let{rects:r,placement:i}=e;return{side:Vu(t,Oi(i),n),align:ki(i)||`center`,anchor:{width:r.reference.width,height:r.reference.height},positioner:{width:r.floating.width,height:r.floating.height}}}function Uu(e){return Wu(e,jl)}function Wu(e,t){let{anchor:n,positionMethod:r=`absolute`,side:i=`bottom`,sideOffset:a=0,align:o=`center`,alignOffset:s=0,collisionBoundary:c,collisionPadding:l=5,sticky:u=!1,arrowPadding:d=5,disableAnchorTracking:f=!1,inline:p,keepMounted:m=!1,floatingRootContext:h,mounted:g,collisionAvoidance:v,shift:y,nodeId:b,adaptiveOrigin:x,lazyFlip:S=!1,externalTree:C}=e,[w,T]=_.useState(null);!g&&w!==null&&T(null);let E=v.side||`flip`,D=v.align||`flip`,O=v.fallbackAxisSide||`end`,k=y?.crossAxis??!1,A=y?.rootBoundary,j=typeof n==`function`?n:void 0,M=K(j),N=j?M:n,P=zo(n),F=zo(g),I=Pu()===`rtl`,L=w||{top:`top`,right:`right`,bottom:`bottom`,left:`left`,"inline-end":I?`left`:`right`,"inline-start":I?`right`:`left`}[i],z=o===`center`?L:`${L}-${o}`,B=l;typeof B==`number`?B={top:B,right:B,bottom:B,left:B}:B&&={top:B.top||0,right:B.right||0,bottom:B.bottom||0,left:B.left||0};let V=+(i===`bottom`),H=+(i===`top`),U=+(i===`right`),W=+(i===`left`),ee={boundary:c===`clipping-ancestors`?`clippingAncestors`:c,padding:B},te=_.useRef(null),G=zo(a),ne=zo(s),re=typeof a==`function`?0:a,ie=typeof s==`function`?0:s,ae=[];p&&ae.push(p),ae.push(zc(e=>{let t=Hu(e,i,I),n=typeof G.current==`function`?G.current(t):G.current,r=typeof ne.current==`function`?ne.current(t):ne.current;return{mainAxis:n,crossAxis:r,alignmentAxis:r}},[re,ie,I,i]));let oe=D===`none`&&E!==`shift`,se=!oe&&(u||k||E===`shift`),ce=E===`none`?null:Hc({...ee,padding:{top:B.top+1+V,right:B.right+1+W,bottom:B.bottom+1+H,left:B.left+1+U},mainAxis:!k&&E===`flip`,crossAxis:D===`flip`&&`alignment`,fallbackAxisSideDirection:O}),le=oe?null:Bc({...ee,rootBoundary:A,mainAxis:D!==`none`,crossAxis:se,limiter:u||k?void 0:Vc(e=>{if(!te.current)return{};let{width:t,height:n}=te.current.getBoundingClientRect(),r=Mi(Oi(e.placement)),i=r===`y`?t:n,a=r===`y`?B.left+B.right:B.top+B.bottom;return{offset:i/2+a/2}})},[ee,u,k,A,B,D]);E===`shift`||D===`shift`||o===`center`?ae.push(le,ce):ae.push(ce,le),ae.push(Uc({...ee,apply({elements:{floating:e},availableWidth:t,availableHeight:n,rects:r}){if(!F.current)return;let i=e.style;i.setProperty(zu,`${t}px`),i.setProperty(Bu,`${n}px`);let a=R(e).devicePixelRatio||1,{x:o,y:s,width:c,height:l}=r.reference,u=(Math.round((o+c)*a)-Math.round(o*a))/a,d=(Math.round((s+l)*a)-Math.round(s*a))/a;i.setProperty(`--anchor-width`,`${u}px`),i.setProperty(`--anchor-height`,`${d}px`)}}),Iu(e=>({element:te.current||Ue(e.elements.floating).createElement(`div`),padding:d,offsetParent:`floating`}),[d]),{name:`transformOrigin`,fn(e){let{elements:t,middlewareData:n,placement:r,rects:o,y:s}=e,c=Oi(r),l=Mi(c),u=te.current,d=n.arrow?.x||0,f=n.arrow?.y||0,p=u?.clientWidth||0,m=u?.clientHeight||0,h=d+p/2,g=f+m/2,_=Math.abs(n.shift?.y||0),v=o.reference.height/2,y=typeof a==`function`?a(Hu(e,i,I)):a,b=_>y,x={top:`${h}px calc(100% + ${y}px)`,bottom:`${h}px ${-y}px`,left:`calc(100% + ${y}px) ${g}px`,right:`${-y}px ${g}px`}[c],S=`${h}px ${o.reference.y+v-s}px`;return t.floating.style.setProperty(`--transform-origin`,se&&l===`y`&&b?S:x),{}}},Lu,x),q(()=>{!g&&h&&h.update({referenceElement:null,floatingElement:null,domReferenceElement:null,positionReference:null})},[g,h]);let ue=_.useMemo(()=>({elementResize:!f&&typeof ResizeObserver<`u`,layoutShift:!f&&typeof IntersectionObserver<`u`}),[f]),{refs:de,elements:fe,x:pe,y:me,middlewareData:he,update:ge,placement:_e,context:ve,isPositioned:ye,floatingStyles:be}=t({rootContext:h,open:m?g:void 0,placement:z,middleware:ae,strategy:r,whileElementsMounted:m?void 0:(...e)=>Ec(...e,ue),nodeId:b,externalTree:C}),{sideX:xe,sideY:Se}=he.adaptiveOrigin||Ru,Ce=ye?r:`fixed`,we=_.useMemo(()=>{let e;return e=ye?x?{position:Ce,[xe]:pe,[Se]:me}:{...be,position:Ce}:{position:Ce,top:0,left:0},e[zu]=`100vw`,e[Bu]=`100vh`,ye||(e.opacity=0),e},[x,Ce,xe,pe,Se,me,be,ye]),Te=_.useRef(null);q(()=>{if(!g)return;let e=P.current,t=typeof e==`function`?e():e,n=(Gu(t)?t.current:t)||null;n!==Te.current&&(de.setPositionReference(n),Te.current=n)},[g,de,N,P]),_.useEffect(()=>{if(!g)return;let e=P.current;typeof e!=`function`&&Gu(e)&&e.current!==Te.current&&(de.setPositionReference(e.current),Te.current=e.current)},[g,de,N,P]),_.useEffect(()=>{if(m&&g&&fe.reference&&fe.floating)return Ec(fe.reference,fe.floating,ge,ue)},[m,g,fe,ge,ue]);let Ee=Oi(_e),De=Vu(i,Ee,I),Oe=ki(_e)||`center`,ke=!!he.hide?.referenceHidden;q(()=>{S&&g&&ye&&Ee!==L&&T(Ee)},[S,g,ye,Ee,L]);let Ae=_.useMemo(()=>({position:`absolute`,top:he.arrow?.y,left:he.arrow?.x}),[he.arrow]),je=he.arrow?.centerOffset!==0;return _.useMemo(()=>({positionerStyles:we,arrowStyles:Ae,arrowRef:te,arrowUncentered:je,side:De,align:Oe,physicalSide:Ee,anchorHidden:ke,refs:de,context:ve,isPositioned:ye,update:ge}),[we,Ae,te,je,De,Oe,Ee,ke,de,ve,ye,ge])}function Gu(e){return e!=null&&`current`in e}function Ku(e){return e===`starting`?os:at}function qu(e,t,{styles:n,transitionStatus:r,props:i,refs:a,hidden:o,inert:s=!1}){let c={...n};return s&&(c.pointerEvents=`none`),lt(`div`,e,{state:t,ref:a,props:[{role:`presentation`,hidden:o,style:c},Ku(r),i],stateAttributesMapping:yu})}var Ju=_.forwardRef(function(e,t){let{render:n,className:r,anchor:i,positionMethod:a=`absolute`,side:o=`top`,align:s=`center`,sideOffset:c=0,alignOffset:l=0,collisionBoundary:u=`clipping-ancestors`,collisionPadding:d=5,arrowPadding:f=5,sticky:p=!1,disableAnchorTracking:m=!1,collisionAvoidance:h=ls,style:g,...v}=e,y=Do(),b=Ou(),x=y.useState(`open`),S=y.useState(`mounted`),C=y.useState(`trackCursorAxis`),w=y.useState(`disableHoverablePopup`),T=y.useState(`floatingRootContext`),E=y.useState(`instantType`),D=y.useState(`transitionStatus`),O=Uu({anchor:i,positionMethod:a,floatingRootContext:T,mounted:S,side:o,sideOffset:c,align:s,alignOffset:l,collisionBoundary:u,collisionPadding:d,sticky:p,arrowPadding:f,disableAnchorTracking:m,keepMounted:b,collisionAvoidance:h,adaptiveOrigin:y.useState(`adaptiveOrigin`)}),k=qu(e,_.useMemo(()=>({open:x,side:O.side,align:O.align,anchorHidden:O.anchorHidden,instant:C===`none`?E:`tracking-cursor`}),[x,O.side,O.align,O.anchorHidden,C,E]),{styles:O.positionerStyles,transitionStatus:D,props:v,refs:[t,y.useStateSetter(`positionerElement`)],hidden:!S,inert:!x||C===`both`||w});return(0,Z.jsx)(ju.Provider,{value:O,children:k})}),Yu=_.forwardRef(function(e,t){let{render:n,className:r,style:i,...a}=e,o=Do(),{side:s,align:c}=Mu(),l=o.useState(`open`),u=o.useState(`instantType`),d=o.useState(`transitionStatus`),f=o.useState(`popupProps`),p=o.useState(`floatingRootContext`),m=o.useState(`disabled`),h=o.useState(`closeDelay`);Ia({open:l,ref:o.context.popupRef,onComplete(){l&&o.context.onOpenChangeComplete?.(!0)}}),Bl(p,{enabled:!m,closeDelay:h});let g=o.useStateSetter(`popupElement`);return lt(`div`,e,{state:{open:l,side:s,align:c,instant:u,transitionStatus:d},ref:[t,o.context.popupRef,g],props:[ol,f,Ku(d),a],stateAttributesMapping:bu})}),Xu=function(e){let{delay:t,closeDelay:n,timeout:r=400}=e,i=_.useMemo(()=>({open:t,close:n}),[t,n]);return(0,Z.jsx)(xu.Provider,{value:t,children:(0,Z.jsx)(Fo,{delay:i,timeoutMs:r,children:e.children})})};function Zu(e){return tt(19)?e:e?`true`:void 0}function Qu(e){let[t,n]=_.useState({current:e,previous:null});return Object.is(e,t.current)||n({current:e,previous:t.current}),t.previous}var $u=_.createContext(void 0);function ed({children:e,container:t}){return(0,Z.jsx)($u.Provider,{value:t,children:e})}function td(e){let t=_.useContext($u);return e??t}function nd({delay:e=0,...t}){return(0,Z.jsx)(Xu,{"data-slot":`tooltip-provider`,delay:e,...t})}function rd({disableHoverablePopup:e=!0,...t}){return(0,Z.jsx)(uu,{"data-slot":`tooltip`,disableHoverablePopup:e,...t})}function id({className:e,...t}){return(0,Z.jsx)(Eu,{className:e,"data-slot":`tooltip-trigger`,...t})}function ad({className:e,side:t=`top`,sideOffset:n=4,align:r=`center`,alignOffset:i=0,children:a,interactive:o=!1,portalContainer:s,...c}){let l=td(s),u=_.useRef(null);return(0,Z.jsx)(Au,{container:l,ref:u,children:(0,Z.jsx)(ed,{container:u,children:(0,Z.jsx)(Ju,{align:r,alignOffset:i,side:t,sideOffset:n,className:`isolate z-50`,children:(0,Z.jsx)(Yu,{"data-slot":`tooltip-content`,className:X(`z-50 inline-flex w-fit max-w-xs origin-(--transform-origin) items-center gap-1.5 rounded-lg border border-[color:color-mix(in_oklab,var(--border)_10%,transparent)] bg-[color:color-mix(in_oklab,var(--muted)_95%,transparent)] px-1.5 py-1 popup-text-xs-plus text-[color:var(--foreground)] shadow-md has-data-[slot=kbd]:pr-1.5 data-[side=bottom]:slide-in-from-top-2 data-[side=inline-end]:slide-in-from-left-2 data-[side=inline-start]:slide-in-from-right-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 **:data-[slot=kbd]:relative **:data-[slot=kbd]:isolate **:data-[slot=kbd]:z-50 **:data-[slot=kbd]:rounded-sm data-[state=delayed-open]:animate-in data-[state=delayed-open]:fade-in-0 data-[state=delayed-open]:zoom-in-95 data-open:animate-in data-open:fade-in-0 data-open:zoom-in-95 data-closed:animate-out data-closed:fade-out-0 data-closed:zoom-out-95`,o?null:`pointer-events-none`,e),...c,children:a})})})})}function od({className:e,...t}){return _.createElement(`label`,{...t,"data-slot":`label`,className:X(`flex items-center gap-2 text-xs/relaxed leading-none font-medium select-none group-data-[disabled=true]:pointer-events-none group-data-[disabled=true]:opacity-50 peer-disabled:cursor-not-allowed peer-disabled:opacity-50`,e)})}var sd=xt(`group/field flex w-full gap-field-control data-[invalid=true]:text-[color:var(--destructive)]`,{variants:{orientation:{vertical:`flex-col *:w-full [&>.sr-only]:w-auto`,horizontal:`flex-row items-center has-[>[data-slot=field-content]]:items-start *:data-[slot=field-label]:flex-auto has-[>[data-slot=field-content]]:[&>[role=checkbox],[role=radio]]:mt-px has-[>[data-slot=field-content]]:[&>[role=radio][data-size=lg]]:mt-0.5`,responsive:`flex-col *:w-full @md/field-group:flex-row @md/field-group:items-center @md/field-group:*:w-auto @md/field-group:has-[>[data-slot=field-content]]:items-start @md/field-group:*:data-[slot=field-label]:flex-auto [&>.sr-only]:w-auto @md/field-group:has-[>[data-slot=field-content]]:[&>[role=checkbox],[role=radio]]:mt-px @md/field-group:has-[>[data-slot=field-content]]:[&>[role=radio][data-size=lg]]:mt-0.5`}},defaultVariants:{orientation:`vertical`}});function cd({className:e,orientation:t=`vertical`,...n}){return(0,Z.jsx)(`div`,{role:`group`,"data-slot":`field`,"data-orientation":t,className:X(sd({orientation:t}),e),...n})}function ld({className:e,...t}){return(0,Z.jsx)(od,{"data-slot":`field-label`,className:X(`group/field-label peer/field-label flex w-fit gap-2 text-[color:color-mix(in_oklab,var(--foreground)_60%,transparent)] leading-snug group-data-[disabled=true]/field:opacity-50 has-data-checked:bg-[color:color-mix(in_oklab,var(--primary)_5%,transparent)] has-[>[data-slot=field]]:rounded-md has-[>[data-slot=field]]:border has-[>[data-slot=field]]:border-[color:color-mix(in_oklab,var(--border)_12%,transparent)] *:data-[slot=field]:p-2 dark:has-data-checked:bg-[color:color-mix(in_oklab,var(--primary)_10%,transparent)]`,`has-[>[data-slot=field]]:w-full has-[>[data-slot=field]]:flex-col group-has-[>[data-slot=checkbox][data-size=sm]]/field:text-xs-plus group-has-[>[data-slot=checkbox][data-checked]]/field:text-[color:var(--foreground)] group-has-[>[data-slot=checkbox][data-size=lg]]/field:text-sm/relaxed group-has-[>[data-slot=radio-group-item][data-size=lg]]/field:text-sm/relaxed`,e),...t})}var ud={down:void 0,left:`rotate-90`,right:`-rotate-90`,up:`rotate-180`};function dd({className:e,direction:t=`down`,openClassName:n,...r}){return(0,Z.jsx)(k,{"aria-hidden":`true`,"data-slot":`primitive-arrow-icon`,className:X(`pointer-events-none shrink-0 size-3.5 text-[color:color-mix(in_oklab,var(--foreground)_60%,transparent)] transition-transform duration-200 ease-out group-hover/button:text-[color:color-mix(in_oklab,var(--foreground)_90%,transparent)] group-active/button:text-[color:color-mix(in_oklab,var(--foreground)_90%,transparent)] group-aria-expanded/button:text-[color:color-mix(in_oklab,var(--foreground)_90%,transparent)] group-aria-pressed/button:text-[color:color-mix(in_oklab,var(--foreground)_90%,transparent)] group-data-open/button:text-[color:color-mix(in_oklab,var(--foreground)_90%,transparent)] group-data-popup-open/button:text-[color:color-mix(in_oklab,var(--foreground)_90%,transparent)] group-data-[state=open]/button:text-[color:color-mix(in_oklab,var(--foreground)_90%,transparent)]`,ud[t],n,e),...r})}var fd={compact:{height:20,intensity:`normal`},default:{height:24,intensity:`medium`},large:{height:48,intensity:`dense`}};function pd(e){return e===`left`||e===`right`}function md(e){return e===`dense`?{fadeStop:90,solidStop:24}:e===`medium`?{fadeStop:82,solidStop:16}:{fadeStop:100,solidStop:0}}function hd(e){return`${Math.max(0,Number(e.toFixed(2)))}px`}function gd({height:e,intensity:t,preset:n}){let r=n?fd[n]:void 0;return{height:e??r?.height??24,intensity:t??r?.intensity??`normal`}}function _d(e){return`linear-gradient(${e===`left`||e===`right`?`to right`:`to bottom`}, transparent 0%, transparent var(--scroll-fade-leading-solid), black var(--scroll-fade-leading-fade), black calc(100% - var(--scroll-fade-trailing-fade)), transparent calc(100% - var(--scroll-fade-trailing-solid)), transparent 100%)`}function vd(e){return e===`bottom`?`top`:e===`top`?`bottom`:e===`left`?`right`:`left`}function yd({intensity:e,showFade:t,size:n}){if(!t)return{fade:`0px`,solid:`0px`};let{fadeStop:r,solidStop:i}=md(e);return e===`normal`?{fade:hd(n),solid:`0px`}:{fade:hd(r/100*n),solid:hd(i/100*n)}}function bd({showOppositeFade:e,showPrimaryFade:t,side:n}){return n===`top`||n===`left`?{leadingFadeVisible:t,trailingFadeVisible:e}:{leadingFadeVisible:e,trailingFadeVisible:t}}function xd({intensity:e,showOppositeFade:t,showPrimaryFade:n,side:r,size:i,style:a}){let o=_d(r),{leadingFadeVisible:s,trailingFadeVisible:c}=bd({showOppositeFade:t,showPrimaryFade:n,side:r}),l=yd({intensity:e,size:i,showFade:s}),u=yd({intensity:e,size:i,showFade:c});return{...a,"--scroll-fade-leading-fade":l.fade,"--scroll-fade-leading-solid":l.solid,"--scroll-fade-mask-image":o,"--scroll-fade-trailing-fade":u.fade,"--scroll-fade-trailing-solid":u.solid}}function Sd(e,t){return e.length===t.length&&e.every((e,n)=>Object.is(e,t[n]))}function Cd(e){let t=(0,_.useRef)(e),n=(0,_.useRef)(0);return Sd(t.current,e)||(t.current=e,n.current+=1),n.current}function wd({dependencyVersion:e,dismissOnFirstInteraction:t,interactionVersion:n}){let[r,i]=(0,_.useState)(!1),a=(0,_.useRef)(n);return(0,_.useLayoutEffect)(()=>{i(!1)},[e,t]),(0,_.useLayoutEffect)(()=>{if(!t){a.current=n;return}a.current!==n&&(a.current=n,i(!0))},[t,n]),{dismissInteraction:(0,_.useCallback)(()=>{i(!0)},[]),interactionDismissed:r}}function Td({interactionDismissed:e,isHorizontal:t,side:n,visibilityMode:r,viewportElement:i}){let a=t?i.scrollLeft:i.scrollTop,o=t?i.clientWidth:i.clientHeight,s=t?i.scrollWidth:i.scrollHeight,c=s>o+1,l=a<=1,u=a+o>=s-1;return e||!c?!1:r===`terminal`?n===`top`||n===`left`?u:l:n===`top`||n===`left`?!l:!u}function Ed({dependencyVersion:e,dismissInteraction:t,dismissOnFirstInteraction:n,interactionDismissed:r,isHorizontal:i,side:a,visibilityMode:o,viewportElement:s}){let[c,l]=(0,_.useState)(!1);return(0,_.useLayoutEffect)(()=>{if(!s){l(!1);return}let e=()=>{let e=Td({interactionDismissed:r,isHorizontal:i,side:a,visibilityMode:o,viewportElement:s});l(t=>t===e?t:e)},c=()=>{if(n){t(),l(!1);return}e()};e(),s.addEventListener(`scroll`,c);let u=null;if(typeof ResizeObserver<`u`){u=new ResizeObserver(e),u.observe(s);let t=s.firstElementChild;t&&u.observe(t)}return()=>{s.removeEventListener(`scroll`,c),u?.disconnect()}},[e,t,n,r,i,a,o,s]),c}function Dd({disableTransition:e,dismissOnFirstInteraction:t,forceVisible:n,height:r,intensity:i,interactionWatch:a,preset:o,showOppositeSide:s,side:c,style:l,visibilityMode:u,viewportElement:d,watch:f}){let p=Cd(f),m=Cd(a),h=pd(c),g=gd({height:r,intensity:i,preset:o}),_=vd(c),{dismissInteraction:v,interactionDismissed:y}=wd({dependencyVersion:p,dismissOnFirstInteraction:t,interactionVersion:m}),b=Ed({dependencyVersion:p,dismissInteraction:v,dismissOnFirstInteraction:t,interactionDismissed:y,isHorizontal:h,side:c,visibilityMode:u,viewportElement:d}),x=Ed({dependencyVersion:p,dismissInteraction:v,dismissOnFirstInteraction:t,interactionDismissed:y,isHorizontal:h,side:_,visibilityMode:u,viewportElement:d}),S=s&&x,C=n||b,w=n||C||S;return{isHorizontal:h,rootStyle:{"--scroll-fade-size":`${g.height}px`},viewportStyle:xd({intensity:g.intensity,showOppositeFade:S,showPrimaryFade:C,side:c,size:g.height,style:e?{...l,transition:`none`}:l}),viewportVisible:w}}function Od({setViewportElement:e,viewportRef:t}){return(0,_.useCallback)(n=>{if(e(n),t){if(typeof t==`function`){t(n);return}t.current=n}},[e,t])}function kd({attachViewport:e,className:t,isHorizontal:n,props:r,scrollBoundaryBehavior:i,side:a,viewportStyle:o,viewportVisible:s,children:c}){let{"data-slot":l,...u}=r;return(0,Z.jsx)(`div`,{...u,className:X(n?`overflow-x-auto overflow-y-hidden`:`overflow-x-hidden overflow-y-auto`,i===`chain`?`overscroll-auto`:`overscroll-contain`,t),"data-scroll-boundary-behavior":i,"data-side":a,"data-slot":l??`scroll-fade-viewport`,"data-scroll-fade-viewport":``,"data-visible":s?`true`:`false`,ref:e,style:o,children:c})}function Ad({children:e,className:t,containerClassName:n,containerRef:r,disableTransition:i=!1,dismissOnFirstInteraction:a=!1,forceVisible:o=!1,height:s,intensity:c,interactionWatch:l=[],preset:u,scrollBoundaryBehavior:d=`contain`,side:f=`bottom`,showOppositeSide:p=!1,style:m,visibilityMode:h=`overflow`,viewportRef:g,watch:v=[],...y}){let[b,x]=(0,_.useState)(null),S=Od({setViewportElement:x,viewportRef:g}),{isHorizontal:C,rootStyle:w,viewportStyle:T,viewportVisible:E}=Dd({disableTransition:i,dismissOnFirstInteraction:a,forceVisible:o,height:s,intensity:c,interactionWatch:l,preset:u,showOppositeSide:p,side:f,style:m,visibilityMode:h,viewportElement:b,watch:v});return(0,Z.jsx)(`div`,{className:X(`relative`,n),"data-slot":`scroll-fade`,ref:r,style:w,children:(0,Z.jsx)(kd,{attachViewport:S,className:t,isHorizontal:C,props:y,scrollBoundaryBehavior:d,side:f,viewportStyle:T,viewportVisible:E,children:e})})}var jd=_.createContext(null),Md=_.createContext(null),Nd=[`flex flex-col pt-2 pb-6 first:border-t-0 data-[toolcraft-section-actions]:first:border-t`,`border-t border-[color:color-mix(in_oklab,var(--border)_8%,transparent)]`,`transition-colors duration-150 ease-out hover:bg-[color:color-mix(in_oklab,var(--foreground)_3%,transparent)]`].join(` `);function Pd({children:e,className:t,...n}){return(0,Z.jsx)(`section`,{...n,className:X(Nd,`group/control-section gap-[14px]`,t),children:e})}function Fd({children:e,className:t}){return(0,Z.jsx)(`div`,{className:X(`flex min-w-0 flex-col gap-[14px]`,t),"data-control-list":``,children:e})}function Id({action:e,collapsed:t=!1,collapsible:n=!1,children:r,collapseLabel:i,expandLabel:a,onCollapsedChange:o}){let s=Ld(r),c=t?a??`展开${s}`:i??`收起${s}`,l=i||a?c:`${c}分组`,u=_.useCallback(()=>{n&&o?.(!t)},[t,n,o]);function d(e){!n||e.key!==`Enter`&&e.key!==` `||(e.preventDefault(),u())}function f(e){e.stopPropagation()}return(0,Z.jsxs)(`div`,{"aria-expanded":n?!t:void 0,"aria-label":n?c:void 0,className:X(`flex h-9 min-w-0 items-center justify-between gap-2 px-3`,n&&`cursor-pointer select-none`),"data-collapsed":n?String(t):void 0,"data-collapsible":n?``:void 0,"data-slot":`control-section-header`,onClick:n?u:void 0,onKeyDown:d,role:n?`button`:void 0,tabIndex:n?0:void 0,children:[(0,Z.jsx)(`div`,{className:`flex min-w-0 items-center gap-1 has-data-[icon-active=true]:[&_[data-slot=panel-title]]:text-[color:var(--link)]`,children:r}),e||n?(0,Z.jsxs)(`div`,{className:`inline-flex shrink-0 items-center gap-1`,onClick:f,onKeyDown:f,onPointerDown:f,children:[e,n?(0,Z.jsxs)(rd,{children:[(0,Z.jsx)(id,{render:(0,Z.jsx)(gr,{"aria-expanded":!t,"aria-label":l,"data-control-section-collapse-button":``,onClick:u,size:`icon-sm`,type:`button`,variant:`ghost`}),children:(0,Z.jsx)(dd,{direction:t?`down`:`up`})}),(0,Z.jsx)(ad,{side:`top`,children:c})]}):null]}):null]})}function Ld(e){let t=Rd(e).trim();return t.length>0?t:`分组`}function Rd(e){return typeof e==`string`||typeof e==`number`?String(e):_.isValidElement(e)?Rd(e.props.children):Array.isArray(e)?e.map(Rd).join(``):``}function zd({allowCompoundDividers:e=!1,children:t,compoundDividerPlacement:n=`both`,flush:r=!1}){let i=n===`both`||n===`top`,a=n===`both`||n===`bottom`;return(0,Z.jsx)(`div`,{className:X(`min-w-0`,!r&&`px-3`,e&&a&&`has-data-[control-section-divider=compound]:relative has-data-[control-section-divider=compound]:pb-[18px] has-data-[control-section-divider=compound]:after:absolute has-data-[control-section-divider=compound]:after:bottom-0 has-data-[control-section-divider=compound]:after:h-px has-data-[control-section-divider=compound]:after:bg-[color:color-mix(in_oklab,var(--border)_8%,transparent)]`,e&&i&&`has-data-[control-section-divider=compound]:pt-[18px] has-data-[control-section-divider=compound]:before:absolute has-data-[control-section-divider=compound]:before:top-0 has-data-[control-section-divider=compound]:before:h-px has-data-[control-section-divider=compound]:before:bg-[color:color-mix(in_oklab,var(--border)_8%,transparent)]`,e&&a&&(r?`has-data-[control-section-divider=compound]:after:inset-x-0`:`has-data-[control-section-divider=compound]:after:inset-x-3`),e&&i&&(r?`has-data-[control-section-divider=compound]:before:inset-x-0`:`has-data-[control-section-divider=compound]:before:inset-x-3`)),"data-control-item-compound-divider-placement":e?n:void 0,"data-control-item-compound-context":e?``:void 0,children:t})}function Bd({children:e}){return(0,Z.jsx)(`p`,{className:`m-0 text-2xs leading-none font-semibold text-[color:color-mix(in_oklab,var(--foreground)_75%,transparent)] uppercase transition-colors duration-150 ease-out`,"data-slot":`panel-title`,children:e})}function Vd(e){let t=_.useContext(jd);return t&&t.label===e?t.action:null}function Hd(e){let t=_.useContext(Md);return t&&t.label===e?t.help:null}function Ud({children:e,className:t,textClassName:n,title:r,...i}){let a=Wd(e),o=Gd(e,a),s=Vd(a),c=Hd(a);return(0,Z.jsxs)(`span`,{className:X(`group/keyframe-control-label inline-flex min-w-0 max-w-full items-center gap-0 has-data-[icon-active=true]:[&_[data-slot=template-field-label-text]]:text-[color:var(--link)] has-data-[icon-active=true]:[&_[data-slot=template-field-label-text]]:opacity-100`,t),"data-control-field-label":``,"data-slot":`field-label`,children:[(0,Z.jsx)(ld,{className:`min-w-0 max-w-full gap-0`,title:r??a,...i,children:(0,Z.jsx)(Ad,{className:`no-scrollbar min-w-0 max-w-full`,containerClassName:`min-w-0 max-w-full`,preset:`compact`,side:`right`,watch:[a??``],children:(0,Z.jsx)(`span`,{className:X(`block whitespace-nowrap opacity-60`,n,`min-w-max`),"data-slot":`template-field-label-text`,title:a,children:o})})}),c?(0,Z.jsxs)(rd,{children:[(0,Z.jsx)(id,{render:(0,Z.jsx)(`button`,{"aria-label":`${a??`Control`} help`,className:`ml-[3px] inline-flex size-3.5 shrink-0 items-center justify-center rounded-full text-[color:color-mix(in_oklab,var(--foreground)_40%,transparent)] transition-colors duration-150 ease-out hover:text-[color:color-mix(in_oklab,var(--foreground)_60%,transparent)] focus-visible:outline-none`,"data-control-field-help":``,type:`button`}),children:(0,Z.jsx)(P,{className:`size-3.5`,weight:`fill`})}),(0,Z.jsx)(ad,{className:`max-w-[240px] whitespace-normal text-left`,side:`top`,children:c})]}):null,s]})}function Wd(e){let t=_.Children.toArray(e).map(e=>typeof e==`string`||typeof e==`number`?String(e):null);if(!(!t.length||t.some(e=>e===null)))return t.join(``).trim()||void 0}function Gd(e,t){if(!t||_.Children.count(e)!==1)return e;let[n]=_.Children.toArray(e);return typeof n!=`string`&&typeof n!=`number`?e:t.replace(/\s+\([^)]{1,80}\)\s*$/u,``).trim()||t}function Kd(e,t){let n=_.useRef(e),r=K(t);q(()=>{n.current!==e&&r(n.current),n.current=e},[e,r])}var qd=_.createContext(void 0);function Jd(){let e=_.useContext(qd);if(e===void 0)throw Error(ze(63));return e}var Yd={...yr,checked(e){return e?{"data-checked":``}:{"data-unchecked":``}}},Xd=_.forwardRef(function(e,t){let{checked:n,className:r,defaultChecked:i,"aria-labelledby":a,form:o,id:s,inputRef:c,name:l,nativeButton:u=!1,onCheckedChange:d,readOnly:f=!1,required:p=!1,disabled:m=!1,render:h,uncheckedValue:g,value:v,style:y,...b}=e,{clearErrors:x}=wr(),{state:S,setTouched:C,setDirty:w,validityData:T,setFilled:E,setFocused:D,validationMode:O,disabled:k,name:A,validation:j}=Sr(),{labelId:M}=jr(),N=k||m,P=A??l,F=_.useRef(null),I=Je(F,c,j.inputRef),L=_.useRef(null),R=kr(),z=Fr({id:s,implicit:!1,controlRef:L}),B=u?void 0:z,[V,H]=Ha({controlled:n,default:!!i,name:`Switch`,state:`checked`});Ua(L,R,V,void 0,!N,l),q(()=>{F.current&&E(F.current.checked)},[E]),Kd(V,()=>{x(P),w(V!==T.initialValue),E(V),j.change(V)});let{getButtonProps:U,buttonRef:W}=Ge({disabled:N,native:u}),ee=Mr(a,M,F,!u,B),te={id:u?z:R,role:`switch`,"aria-checked":V,"aria-readonly":f||void 0,"aria-required":p||void 0,"aria-labelledby":ee,onFocus(){N||D(!0)},onBlur(){let e=F.current;!e||N||(C(!0),D(!1),O===`onBlur`&&j.commit(e.checked))},onClick(e){if(f||N)return;e.preventDefault();let t=F.current;t&&We(t,e)}},G={...j.getValidationProps(N),checked:V,disabled:N,form:o,id:B,name:P,required:p,style:P?Uo:Ho,tabIndex:-1,type:`checkbox`,"aria-hidden":!0,ref:I,onChange(e){if(e.nativeEvent.defaultPrevented)return;if(f){e.preventDefault();return}let t=e.currentTarget.checked,n=$(Wa,e.nativeEvent);d?.(t,n),!n.isCanceled&&H(t)},onClick(e){e.stopPropagation()},onFocus(){L.current?.focus()},...v===void 0?at:{value:v}},ne=_.useMemo(()=>({...S,checked:V,disabled:N,readOnly:f,required:p}),[S,V,N,f,p]),re=lt(`span`,e,{state:ne,ref:[t,L,W],props:[te,b,U,e=>j.getValidationProps(N,e)],stateAttributesMapping:Yd});return(0,Z.jsxs)(qd.Provider,{value:ne,children:[re,!V&&P&&g!==void 0&&(0,Z.jsx)(`input`,{type:`hidden`,form:o,name:P,value:g,disabled:N}),(0,Z.jsx)(`input`,{...G,suppressHydrationWarning:!0})]})}),Zd=_.forwardRef(function(e,t){let{render:n,className:r,style:i,...a}=e;return lt(`span`,e,{state:Jd(),ref:t,stateAttributesMapping:Yd,props:a})});function Qd({className:e,checkedThumbSide:t=`end`,size:n=`default`,...r}){return(0,Z.jsx)(Xd,{"data-checked-thumb-side":t,"data-slot":`switch`,"data-size":n,className:X(`peer group/switch relative inline-flex shrink-0 cursor-pointer items-center rounded-full p-px transition-all outline-none after:absolute after:-inset-x-3 after:-inset-y-2 aria-invalid:ring aria-invalid:ring-[color:color-mix(in_oklab,var(--destructive)_20%,transparent)] data-[size=default]:h-4 data-[size=default]:w-[28px] data-[size=sm]:h-3.5 data-[size=sm]:w-[24px] data-[size=xs]:h-3 data-[size=xs]:w-5 dark:aria-invalid:ring-[color:color-mix(in_oklab,var(--destructive)_40%,transparent)] data-checked:bg-[color:var(--accent)] data-unchecked:bg-[color:color-mix(in_oklab,var(--input)_20%,transparent)] data-disabled:cursor-not-allowed data-disabled:opacity-50`,e),...r,children:(0,Z.jsx)(Zd,{"data-slot":`switch-thumb`,className:`pointer-events-none block rounded-full bg-[color:var(--background)] ring-0 transition-transform group-data-[size=default]/switch:size-3.5 group-data-[size=sm]/switch:size-3 group-data-[size=xs]/switch:size-2.5 group-data-[checked-thumb-side=end]/switch:data-checked:translate-x-[calc(100%-2px)] group-data-[checked-thumb-side=end]/switch:data-unchecked:translate-x-0 group-data-[checked-thumb-side=start]/switch:data-checked:translate-x-0 group-data-[checked-thumb-side=start]/switch:data-unchecked:translate-x-[calc(100%-2px)] dark:bg-[color:var(--foreground)]`})})}function $d({checked:e,onCheckedChange:t}){let[n,r]=_.useState(e);return _.useEffect(()=>{r(e)},[e]),[n,e=>{r(e),t?.(e)}]}function ef({checked:e,disabled:t=!1,name:n,onCheckedChange:r,showLabel:i=!0}){let[a,o]=$d({checked:e,onCheckedChange:r});return(0,Z.jsxs)(cd,{className:`h-fit justify-start py-1`,orientation:`horizontal`,style:{gap:8},children:[(0,Z.jsx)(Qd,{"aria-label":n,checked:a,disabled:t,onCheckedChange:o,size:`default`}),i?(0,Z.jsx)(Ud,{textClassName:`opacity-90`,children:n}):null]})}var tf=xt(`flex w-fit items-stretch *:focus:relative *:focus:z-10 *:focus-visible:relative *:focus-visible:z-10 has-[>[data-slot=button-group]]:gap-2 has-[select[aria-hidden=true]:last-child]:[&>[data-slot=select-trigger]:last-of-type]:rounded-r-md [&>[data-slot]]:relative [&>[data-slot=select-trigger]:not([class*='w-'])]:w-fit [&>input]:flex-1`,{variants:{orientation:{horizontal:`*:data-slot:rounded-r-none [&>[data-slot]:not(:has(~[data-slot]))]:rounded-r-md! [&>[data-slot]~[data-slot]]:rounded-l-none [&>[data-slot]:has(~[data-slot])]:border-r-0`,vertical:`flex-col *:data-slot:rounded-b-none [&>[data-slot]:not(:has(~[data-slot]))]:rounded-b-md! [&>[data-slot]~[data-slot]]:rounded-t-none [&>[data-slot]:has(~[data-slot])]:border-b-0`},adjacentBorderTone:{default:null,subtle:null}},compoundVariants:[{adjacentBorderTone:`default`,className:`[&>[data-slot]:not([data-slot=button-group-separator]):hover+[data-slot]]:!border-l-[color:color-mix(in_oklab,var(--border)_20%,transparent)] [&>[data-slot]:not([data-slot=button-group-separator]):focus+[data-slot]]:!border-l-[color:color-mix(in_oklab,var(--border)_30%,transparent)] [&>[data-slot]:not([data-slot=button-group-separator])[aria-expanded=true]+[data-slot]]:!border-l-[color:color-mix(in_oklab,var(--border)_45%,transparent)] [&>[data-slot]:not([data-slot=button-group-separator])[data-open]+[data-slot]]:!border-l-[color:color-mix(in_oklab,var(--border)_45%,transparent)] [&>[data-slot]:not([data-slot=button-group-separator])[data-popup-open]+[data-slot]]:!border-l-[color:color-mix(in_oklab,var(--border)_45%,transparent)]`,orientation:`horizontal`},{adjacentBorderTone:`subtle`,className:`[&>[data-slot]:not([data-slot=button-group-separator]):hover+[data-slot]]:!border-l-[color:color-mix(in_oklab,var(--border)_20%,transparent)] [&>[data-slot]:not([data-slot=button-group-separator]):focus+[data-slot]]:!border-l-[color:color-mix(in_oklab,var(--border)_30%,transparent)] [&>[data-slot]:not([data-slot=button-group-separator])[aria-expanded=true]+[data-slot]]:!border-l-[color:color-mix(in_oklab,var(--border)_30%,transparent)] [&>[data-slot]:not([data-slot=button-group-separator])[data-open]+[data-slot]]:!border-l-[color:color-mix(in_oklab,var(--border)_30%,transparent)] [&>[data-slot]:not([data-slot=button-group-separator])[data-popup-open]+[data-slot]]:!border-l-[color:color-mix(in_oklab,var(--border)_30%,transparent)]`,orientation:`horizontal`},{adjacentBorderTone:`default`,className:`[&>[data-slot]:not([data-slot=button-group-separator]):hover+[data-slot]]:!border-t-[color:color-mix(in_oklab,var(--border)_20%,transparent)] [&>[data-slot]:not([data-slot=button-group-separator]):focus+[data-slot]]:!border-t-[color:color-mix(in_oklab,var(--border)_30%,transparent)] [&>[data-slot]:not([data-slot=button-group-separator])[aria-expanded=true]+[data-slot]]:!border-t-[color:color-mix(in_oklab,var(--border)_45%,transparent)] [&>[data-slot]:not([data-slot=button-group-separator])[data-open]+[data-slot]]:!border-t-[color:color-mix(in_oklab,var(--border)_45%,transparent)] [&>[data-slot]:not([data-slot=button-group-separator])[data-popup-open]+[data-slot]]:!border-t-[color:color-mix(in_oklab,var(--border)_45%,transparent)]`,orientation:`vertical`},{adjacentBorderTone:`subtle`,className:`[&>[data-slot]:not([data-slot=button-group-separator]):hover+[data-slot]]:!border-t-[color:color-mix(in_oklab,var(--border)_20%,transparent)] [&>[data-slot]:not([data-slot=button-group-separator]):focus+[data-slot]]:!border-t-[color:color-mix(in_oklab,var(--border)_30%,transparent)] [&>[data-slot]:not([data-slot=button-group-separator])[aria-expanded=true]+[data-slot]]:!border-t-[color:color-mix(in_oklab,var(--border)_30%,transparent)] [&>[data-slot]:not([data-slot=button-group-separator])[data-open]+[data-slot]]:!border-t-[color:color-mix(in_oklab,var(--border)_30%,transparent)] [&>[data-slot]:not([data-slot=button-group-separator])[data-popup-open]+[data-slot]]:!border-t-[color:color-mix(in_oklab,var(--border)_30%,transparent)]`,orientation:`vertical`}],defaultVariants:{adjacentBorderTone:`default`,orientation:`horizontal`}});function nf({adjacentBorderTone:e,className:t,orientation:n,...r}){return(0,Z.jsx)(`div`,{role:`group`,"data-slot":`button-group`,"data-orientation":n,className:X(tf({adjacentBorderTone:e,orientation:n}),t),...r})}function rf(e,t=-(2**53-1),n=2**53-1){return Math.max(t,Math.min(e,n))}function af(e,t,n=(e,t)=>e===t){return e.length===t.length&&e.every((e,r)=>n(e,t[r]))}var of=_.createContext({register:()=>{},unregister:()=>{},subscribeMapChange:()=>()=>{},nextIndexRef:{current:0}});function sf(){return _.useContext(of)}function cf(e){let{children:t,elementsRef:n,labelsRef:r,onMapChange:i}=e,a=K(i),[,o]=_.useState(!1),s=_e(uf).current,c=_e(lf).current,l=_.useRef(0),u=_.useRef(!0),d=_.useRef([]),f=_.useRef(null),p=K(()=>{u.current||(u.current=!0,o(e=>!e))}),m=K((e,t)=>{c.set(e,t),p()}),h=K(e=>{c.delete(e),p()}),g=K(e=>{let t=new Map;return n.current.length=0,r&&(r.current.length=0),e.forEach(e=>{t.set(e.element,{...e.registration.metadata??{},index:e.index}),n.current[e.index]=e.element,r&&(r.current[e.index]=e.registration.label===void 0?e.registration.textRef?.current?.textContent??e.element.textContent:e.registration.label)}),l.current=n.current.length,t});function v(e){if(f.current?.disconnect(),f.current=null,typeof MutationObserver!=`function`||e.length<2)return;let t=new MutationObserver(n=>{if(!pf(n))return;let r=null;for(let n of e)if(n.isConnected){if(r&&mf(r,n)>0){t.disconnect(),p();return}r=n}});f.current=t;let n=new Set;for(let t=1;t<e.length;t+=1){let r=ff(e[t-1],e[t]);r&&n.add(r)}n.forEach(e=>t.observe(e,{childList:!0}))}let y=K(()=>{let[e,t]=df(c),n=g(e);v(t),d.current=e,u.current=!1,s.forEach(e=>e(n)),a(n)});q(()=>(u.current||g(d.current),()=>{n.current=[],r&&(r.current=[])}),[n,r,g]),q(()=>{u.current&&y()}),q(()=>()=>{f.current?.disconnect(),u.current=!0},[]);let b=K(e=>(s.add(e),()=>{s.delete(e)})),x=_.useMemo(()=>({register:m,unregister:h,subscribeMapChange:b,nextIndexRef:l}),[m,h,b,l]);return(0,Z.jsx)(of.Provider,{value:x,children:t})}function lf(){return new Map}function uf(){return new Set}function df(e){let t=new Set,n=[],r=[];e.forEach((e,i)=>{if(!i.isConnected)return;let a=e.index,o={index:a??-1,element:i,registration:e};a===null?r.push(o):a>=0&&(t.add(a),n.push(o))});let i=0;return r.sort((e,t)=>mf(e.element,t.element)),r.forEach(e=>{for(;t.has(i);)i+=1;e.index=i,n.push(e),i+=1}),t.size>0&&n.sort((e,t)=>e.index-t.index),[n,r.map(e=>e.element)]}function ff(e,t){let n=e.parentElement;for(;n&&!n.contains(t);)n=n.parentElement;return n}function pf(e){for(let t of e)for(let e=0;e<t.removedNodes.length;e+=1)if(t.removedNodes[e].isConnected)return!0;return!1}function mf(e,t){return e.compareDocumentPosition(t)&Node.DOCUMENT_POSITION_FOLLOWING?-1:1}function hf(e){return e==null?void 0:`${e}-label`}function gf(e,t){return e??t}function _f(e,t){return e-t}function vf(e,t,n,r,i,a){let o=rf(e,n,r);if(!i)return o;let s=a.slice();return s[t]=rf(o,a[t-1]??-1/0,a[t+1]??1/0),s.sort(_f)}function yf(e,t,n){if(!Array.isArray(e))return!0;let r=t*n;for(let t=0;t<e.length-1;t+=1)if(!(Math.abs(e[t]-e[t+1])>=r))return!1;return!0}var bf=()=>null,xf={activeThumbIndex:bf,max:bf,min:bf,minStepsBetweenValues:bf,step:bf,values:bf,...yr},Sf=_.createContext(void 0);function Cf(){let e=_.useContext(Sf);if(e===void 0)throw Error(ze(62));return e}function wf(e,t){return e===t||Array.isArray(e)&&Array.isArray(t)&&af(e,t)}var Tf=_.forwardRef(function(e,t){let{"aria-labelledby":n,className:r,defaultValue:i,disabled:a=!1,id:o,format:s,largeStep:c=10,locale:l,render:u,max:d=100,min:f=0,minStepsBetweenValues:p=0,form:m,name:h,onValueChange:g,onValueCommitted:v,orientation:y=`horizontal`,step:b=1,thumbCollisionBehavior:x=`push`,thumbAlignment:S=`center`,value:C,style:w,...T}=e,E=kr(o),D=hf(E),O=K(g),k=K(v),{clearErrors:A}=wr(),{state:j,disabled:M,name:N,setTouched:P,setDirty:F,validityData:I,validation:L}=Sr(),{labelId:R}=jr(),[z,B]=_.useState(),V=n??gf(R,z),H=M||a,U=N??h,[W,ee]=Ha({controlled:C,default:i??f,name:`Slider`}),te=_.useRef(null),G=_.useRef(null),ne=_.useRef([]),re=_.useRef(null),ie=_.useRef(-1),ae=_.useRef(null),oe=_.useRef(Wa),[se,ce]=_.useState(-1),[le,ue]=_.useState(-1),[de,fe]=_.useState(!1),[pe,me]=_.useState(()=>new Map),[he,ge]=_.useState([void 0,void 0]),_e=K(e=>{ce(e),e!==-1&&ue(e)}),ve=K(e=>{e&&(G.current=e)}),ye=Array.isArray(W),be=_.useMemo(()=>ye?W.map(e=>rf(e,f,d)).sort(_f):[rf(W,f,d)],[d,f,ye,W]),xe=ye?be:be[0];Ua(L.inputRef,E,xe,void 0,!H,h),Kd(xe,()=>{A(U),L.change(xe);let e=I.initialValue,t;t=Array.isArray(xe)&&Array.isArray(e)?!af(xe,e):xe!==e,F(t)});let Se=K((e,t)=>{if(Number.isNaN(e)||wf(e,W))return!1;let n=t.event,r=n.constructor,i=new r(n.type,n);return Object.defineProperty(i,"target",{writable:!0,value:{value:e,name:U}}),t.event=i,O(e,t),!t.isCanceled&&(oe.current=t.reason,ee(e),!0)}),Ce=K((e,t,n)=>{let r=vf(e,t,f,d,ye,be);if(yf(r,b,p)){let e=`key`in n?no:Qa,i=Se(r,$(e,n.nativeEvent,void 0,{activeThumbIndex:t}));P(!0),i&&k(r,uo(e,n.nativeEvent))}});q(()=>{if(!H)return;let e=ni(Ue(te.current));Q(te.current,e)&&e.blur(),se!==-1&&_e(-1)},[se,H,_e]);let we=_.useMemo(()=>({...j,activeThumbIndex:se,disabled:H,dragging:de,orientation:y,max:d,min:f,minStepsBetweenValues:p,step:b,values:be}),[j,se,H,de,d,f,p,y,b,be]),Te=_.useMemo(()=>({active:se,controlRef:G,disabled:H,dragging:de,validation:L,format:s,handleInputChange:Ce,indicatorPosition:he,inset:S!==`center`,labelId:V,rootLabelId:D,largeStep:c,lastUsedThumbIndex:le,lastChangeReasonRef:oe,form:m,locale:l,max:d,min:f,minStepsBetweenValues:p,name:U,onValueCommitted:k,orientation:y,pressedThumbCenterOffsetRef:re,pressedThumbIndexRef:ie,pressedValuesRef:ae,registerFieldControlRef:ve,renderBeforeHydration:S===`edge`,setActive:_e,setDragging:fe,setIndicatorPosition:ge,setLabelId:B,setValue:Se,state:we,step:b,thumbCollisionBehavior:x,thumbMap:pe,thumbRefs:ne,values:be}),[se,V,D,H,de,L,s,Ce,he,c,le,m,l,d,f,p,U,k,y,ve,_e,Se,we,b,x,S,pe,be]),Ee=lt(`div`,e,{state:we,ref:[t,te],props:[{"aria-labelledby":V,id:E,role:`group`},T,e=>L.getValidationProps(H,e)],stateAttributesMapping:xf});return(0,Z.jsx)(Sf.Provider,{value:Te,children:(0,Z.jsx)(cf,{elementsRef:ne,onMapChange:me,children:Ee})})});function Ef(e){return Array.isArray(e)?e.map(e=>Ef(e)).join(`,`):e==null?``:String(e)}var Df=new Map;function Of(e,t){let n=JSON.stringify({locale:Ef(e),options:t}),r=Df.get(n);if(r)return r;let i=new Intl.NumberFormat(e,t);return Df.set(n,i),i}function kf(e,t,n){return e==null?``:Of(t,n).format(e)}function Af(e,t){let n=e.getBoundingClientRect();return t?(n.top+n.bottom)/2:(n.left+n.right)/2}function jf(e){if(e===0)return 0;if(Math.abs(e)<1){let t=e.toExponential().split(`e-`),n=t[0].split(`.`)[1];return(n?n.length:0)+parseInt(t[1],10)}let t=e.toString().split(`.`)[1];return t?t.length:0}function Mf(e,t,n){let r=Math.round((e-n)/t)*t+n;return Number(r.toFixed(Math.max(jf(t),jf(n))))}function Nf(e,t,n,r,i,a,o,s){let c=e.slice(),l=a*o,u=c.length-1,d=s??e;c[t]=rf(n,r+t*l,i-(u-t)*l);for(let e=t+1;e<=u;e+=1){let t=c[e-1]+l,n=i-(u-e)*l,r=d[e],a=Math.max(c[e],t);r<a&&(a=Math.max(r,t)),c[e]=rf(a,t,n)}for(let e=t-1;e>=0;--e){let t=c[e+1]-l,n=r+e*l,i=d[e],a=Math.min(c[e],t);i>a&&(a=Math.min(i,t)),c[e]=rf(a,n,t)}for(let e=0;e<=u;e+=1)c[e]=Number(c[e].toFixed(12));return c}function Pf(e,t,n,r,i,a,o,s,c,l){let u=n??t,d=r??t;if(!(u.length>1))return{value:a,thumbIndex:0,didSwap:!1};let f=c*l;if(e===`push`)return{value:Nf(u,i,a,o,s,c,l),thumbIndex:i,didSwap:!1};let p=u.slice(),m=p[i-1],h=p[i+1],g=m==null?o:m+f,_=h==null?s:h-f,v=Number(rf(a,g,_).toFixed(12));switch(p[i]=v,e){case`swap`:{let e=u[i],t=1e-7,n=a>e,r=a<e,g=n&&h!=null&&a>=h-t,_=r&&m!=null&&a<=m+t;if(!g&&!_)return{value:p,thumbIndex:i,didSwap:!1};let y=g?i+1:i-1,b=p.map((e,t)=>t===i?v:d[t]??u[t]),x=a;x=g?Math.max(a,p[y]):Math.min(a,p[y]);let S=Nf(p,y,x,o,s,c,l,b),C=g?y-1:y+1,w=S[C-1],T=S[C+1],E=w==null?o:w+f;E=Math.max(E,o+C*f);let D=T==null?s:T-f;D=Math.min(D,s-(S.length-1-C)*f);let O=rf(v,E,D);return S[C]=Number(O.toFixed(12)),{value:S,thumbIndex:y,didSwap:!0}}default:return{value:p,thumbIndex:i,didSwap:!1}}}var Ff=2;function If(e,t){if(!e)return{start:0,end:0};function n(e){let t=e==null?0:parseFloat(e);return Number.isNaN(t)?0:t}let r=t?`Top`:`InlineStart`,i=t?`Bottom`:`InlineEnd`;return{start:n(e[`border${r}Width`])+n(e[`padding${r}`]),end:n(e[`border${i}Width`])+n(e[`padding${i}`])}}function Lf(e,t){if(t.current!=null&&e.changedTouches){let n=e;for(let e=0;e<n.changedTouches.length;e+=1){let r=n.changedTouches[e];if(r.identifier===t.current)return{x:r.clientX,y:r.clientY}}return null}return{x:e.clientX,y:e.clientY}}var Rf=_.forwardRef(function(e,t){let{render:n,className:r,style:i,...a}=e,{disabled:o,dragging:s,inset:c,lastChangeReasonRef:l,max:u,min:d,minStepsBetweenValues:f,onValueCommitted:p,orientation:m,pressedThumbCenterOffsetRef:h,pressedThumbIndexRef:g,pressedValuesRef:v,registerFieldControlRef:y,renderBeforeHydration:b,setActive:x,setDragging:S,setValue:C,state:w,step:T,thumbCollisionBehavior:E,thumbRefs:D,values:O}=Cf(),k=Pu(),A=O.length>1,j=m===`vertical`,M=_.useRef(null),N=_.useRef(null),P=K(e=>{e&&N.current==null&&(N.current=R(e).getComputedStyle(e))}),F=_.useRef(null),I=_.useRef(0),L=_.useRef(0),z=_.useRef(null),B=zo(O);function H(e){return e?.querySelector(`input[type="range"]`)}function U(e){g.current=e,D.current[e]||(h.current=null)}function W(){g.current=-1,h.current=null}function ee(e){return V(e)?D.current.some(t=>!V(t)||!Q(t,e)?!1:H(t)?.disabled===!0):!1}function te(e){let t=M.current,n=g.current;if(!t||n<0||n>=O.length)return n>=O.length&&(z.current=null),null;let{width:r,height:i,bottom:a,left:o,right:s}=t.getBoundingClientRect(),c=If(N.current,j),l=L.current,p=(j?i:r)-c.start-c.end-l*2,m=h.current??0,_=e.x-m,y=e.y-m,b=rf(((j?a-y-c.end:(k===`rtl`?s-_:_-o)-c.start)-l)/p,0,1),x=(u-d)*b+d;return x=Mf(x,T,d),x=rf(x,d,u),A?Pf(E,O,B.current,v.current,n,x,d,u,T,f):{value:x,thumbIndex:n,didSwap:!1}}function G(e){v.current=A?O.slice():null,z.current=null,B.current=O;let t=g.current,n=t;if(t>-1&&t<O.length){if(O[t]===u){let e=t;for(;e>0&&O[e-1]===u;)--e;n=e}}else{let t=j?`y`:`x`,r;n=-1;for(let i=0;i<D.current.length;i+=1){let a=D.current[i];if(V(a)&&!H(a)?.disabled){let o=Af(a,j),s=Math.abs(e[t]-o);(r===void 0||s<=r)&&(n=i,r=s)}}}if(n>-1&&n!==t&&U(n),c){let e=D.current[n];if(V(e)){let t=e.getBoundingClientRect();L.current=t[j?`height`:`width`]/2}}}function ne(e){let t=H(D.current?.[e]);t&&t.focus({preventScroll:!0,focusVisible:!1})}function re(e,t,n){let r=C(e.value,$(t,n,void 0,{activeThumbIndex:e.thumbIndex}));return r&&(z.current=e.value,B.current=Array.isArray(e.value)?e.value:[e.value],e.didSwap&&(U(e.thumbIndex),ne(e.thumbIndex))),r}let ie=K(e=>{let t=Lf(e,F);if(t==null)return;if(I.current+=1,e.type===`pointermove`&&e.buttons===0){ae(e);return}let n=te(t);n!=null&&yf(n.value,T,f)&&(!s&&I.current>Ff&&S(!0),re(n,ro,e))}),ae=K(e=>{x(-1),S(!1),h.current=null;let t=z.current;if(Array.isArray(t)&&t.length!==O.length&&(z.current=null),z.current!=null){let t=l.current;p(z.current,uo(t,e))}`pointerType`in e&&M.current?.hasPointerCapture(e.pointerId)&&M.current?.releasePointerCapture(e.pointerId),g.current=-1,F.current=null,se()}),oe=K(e=>{if(o)return;if(ee(ri(e))){W();return}let t=e.changedTouches[0];if(t==null)return;F.current=t.identifier;let n={x:t.clientX,y:t.clientY};G(n);let r=te(n);if(r==null)return;ne(r.thumbIndex),re(r,Za,e),I.current=0;let i=Ue(M.current);i.addEventListener(`touchmove`,ie,{passive:!0}),i.addEventListener(`touchend`,ae,{passive:!0})}),se=K(()=>{let e=Ue(M.current);e.removeEventListener(`pointermove`,ie),e.removeEventListener(`pointerup`,ae),e.removeEventListener(`touchmove`,ie),e.removeEventListener(`touchend`,ae),v.current=null,z.current=null}),ce=Ma();return _.useEffect(()=>{let e=M.current;if(!e)return()=>se();let t=Lo(e,`touchstart`,oe,{passive:!0});return()=>{t(),ce.cancel(),se()}},[se,oe,M,ce]),_.useEffect(()=>{o&&se()},[o,se]),lt(`div`,e,{state:w,ref:[t,y,M,P],props:[{"data-base-ui-slider-control":b?``:void 0,onPointerDown(e){let t=M.current,n=ri(e.nativeEvent);if(!t||o||e.defaultPrevented||!V(n)||e.button!==0)return;if(ee(n)){W();return}let r={x:e.clientX,y:e.clientY};G(r);let i=te(r);if(i==null)return;Q(D.current[i.thumbIndex],ni(Ue(t)))?e.preventDefault():ce.request(()=>{ne(i.thumbIndex)}),S(!0),h.current??re(i,Za,e.nativeEvent),e.nativeEvent.pointerId&&t.setPointerCapture(e.nativeEvent.pointerId),I.current=0;let a=Ue(t);a.addEventListener(`pointermove`,ie,{passive:!0}),a.addEventListener(`pointerup`,ae,{once:!0})}},a],stateAttributesMapping:xf})}),zf=_.forwardRef(function(e,t){let{render:n,className:r,style:i,...a}=e,{state:o}=Cf();return lt(`div`,e,{state:o,ref:t,props:[{style:{position:`relative`}},a],stateAttributesMapping:xf})});function Bf(){return rt}function Vf(){return!1}function Hf(){return!0}function Uf(){return(0,Jc.useSyncExternalStore)(Bf,Vf,Hf)}function Wf(e,t,n){return(e-t)*100/(n-t)}var Gf=`ArrowUp`,Kf=`ArrowDown`,qf=`ArrowLeft`,Jf=`ArrowRight`,Yf=`Home`,Xf=`PageUp`,Zf=`PageDown`,Qf=new Set([Gf,Kf,qf,Jf,Yf,`End`]),$f=[`Shift`,`Control`,`Alt`,`Meta`];function ep(e){return H(e)&&e.tagName===`INPUT`}function tp(e){return!!(ep(e)&&e.selectionStart!=null||H(e)&&e.tagName===`TEXTAREA`)}function np(e,t,n,r){if(!e||!t||!t.scrollTo)return;let i=e.scrollLeft,a=e.scrollTop,o=e.clientWidth<e.scrollWidth,s=e.clientHeight<e.scrollHeight;if(o&&r!==`vertical`){let r=rp(e,t,`left`),a=ip(e),o=ip(t);n===`ltr`&&(r+t.offsetWidth+o.scrollMarginRight>e.scrollLeft+e.clientWidth-a.scrollPaddingRight?i=r+t.offsetWidth+o.scrollMarginRight-e.clientWidth+a.scrollPaddingRight:r-o.scrollMarginLeft<e.scrollLeft+a.scrollPaddingLeft&&(i=r-o.scrollMarginLeft-a.scrollPaddingLeft)),n===`rtl`&&(r-o.scrollMarginLeft<e.scrollLeft+a.scrollPaddingLeft?i=r-o.scrollMarginLeft-a.scrollPaddingLeft:r+t.offsetWidth+o.scrollMarginRight>e.scrollLeft+e.clientWidth-a.scrollPaddingRight&&(i=r+t.offsetWidth+o.scrollMarginRight-e.clientWidth+a.scrollPaddingRight))}if(s&&r!==`horizontal`){let n=rp(e,t,`top`),r=ip(e),i=ip(t);n-i.scrollMarginTop<e.scrollTop+r.scrollPaddingTop?a=n-i.scrollMarginTop-r.scrollPaddingTop:n+t.offsetHeight+i.scrollMarginBottom>e.scrollTop+e.clientHeight-r.scrollPaddingBottom&&(a=n+t.offsetHeight+i.scrollMarginBottom-e.clientHeight+r.scrollPaddingBottom)}e.scrollTo({left:i,top:a,behavior:`auto`})}function rp(e,t,n){let r=n===`left`?`offsetLeft`:`offsetTop`,i=0;for(;t.offsetParent&&(i+=t[r],t.offsetParent!==e);)t=t.offsetParent;return i}function ip(e){let t=getComputedStyle(e);return{scrollMarginTop:parseFloat(t.scrollMarginTop)||0,scrollMarginRight:parseFloat(t.scrollMarginRight)||0,scrollMarginBottom:parseFloat(t.scrollMarginBottom)||0,scrollMarginLeft:parseFloat(t.scrollMarginLeft)||0,scrollPaddingTop:parseFloat(t.scrollPaddingTop)||0,scrollPaddingRight:parseFloat(t.scrollPaddingRight)||0,scrollPaddingBottom:parseFloat(t.scrollPaddingBottom)||0,scrollPaddingLeft:parseFloat(t.scrollPaddingLeft)||0}}function ap(e={}){let{guess:t,label:n,metadata:r,textRef:i,index:a}=e,{register:o,unregister:s,subscribeMapChange:c,nextIndexRef:l}=sf(),u=_.useRef(-1),[d,f]=_.useState(a==null&&t?()=>{if(u.current===-1){let e=l.current;l.current+=1,u.current=e}return u.current}:-1),p=a??d,m=_.useRef(null),h=_.useCallback(e=>{let t=m.current;t&&s(t),m.current=e,e&&o(e,{metadata:r??null,index:a??null,label:n,textRef:i})},[a,o,s,r,n,i]);return q(()=>{if(a==null)return c(e=>{let t=m.current?e.get(m.current)?.index:null;t!=null&&f(t)})},[a,c]),{ref:h,index:p}}var op=_.createContext(void 0),sp={disableStyleElements:!1};function cp(){return _.useContext(op)??sp}function lp(e){let{script:t}=e,{nonce:n}=cp();return Uf()?(0,Z.jsx)(`script`,{nonce:n,dangerouslySetInnerHTML:{__html:t},suppressHydrationWarning:!0}):null}var up,dp=new Set([...Qf,Xf,Zf]);function fp(e,t,n,r){if(!(t<0))return e.length===2?`${kf(e[t],r,n)} ${t===0?`start`:`end`} range`:n?kf(e[t],r,n):void 0}function pp(e,t,n,r,i){let a=e+t*n;return rf(Number(a.toFixed(Math.max(jf(e),jf(t),jf(r)))),r,i)}var mp=_.forwardRef(function(e,t){let{render:n,children:r,className:i,"aria-describedby":a,"aria-label":o,"aria-labelledby":s,"aria-valuetext":c,disabled:l=!1,getAriaLabel:u,getAriaValueText:d,id:f,index:p,inputRef:m,onBlur:h,onFocus:g,onKeyDown:v,tabIndex:y,style:b,...x}=e,S=kr(f),{active:C,lastUsedThumbIndex:w,controlRef:T,disabled:E,validation:D,format:O,handleInputChange:k,inset:A,labelId:j,largeStep:M,locale:N,max:P,min:F,minStepsBetweenValues:I,form:L,name:z,orientation:B,pressedThumbCenterOffsetRef:V,pressedThumbIndexRef:H,renderBeforeHydration:U,setActive:W,setIndicatorPosition:ee,state:te,step:G,thumbRefs:ne,values:re}=Cf(),ie=Pu(),ae=l||E,oe=re.length>1,se=B===`vertical`,ce=ie===`rtl`,{setTouched:le,setFocused:ue,validationMode:de}=Sr(),fe=_.useRef(null),pe=_.useRef(null),me=_.useRef(!1),he=K(e=>{me.current||g?.(e)}),ge=K(e=>{me.current||h?.(e)}),_e=kr(),ve=Fr(),ye=oe?_e:ve,{ref:be,index:xe}=ap({metadata:_.useMemo(()=>({inputId:ye}),[ye])}),Se=oe?p??xe:0,Ce=Se===re.length-1,Te=re[Se],Ee=Wf(Te,F,P),[De,Oe]=_.useState(),ke=Uf(),Ae=w>=0&&w<re.length?w:-1,je=K(()=>{let e=T.current,t=fe.current;if(!e||!t)return;let n=t.getBoundingClientRect(),r=e.getBoundingClientRect(),i=se?`height`:`width`,a=r[i]-n[i],o=(n[i]/2+a*Ee/100)/r[i]*100,s=Number.isFinite(o)?o:void 0;Oe(s),Se===0?ee(e=>[s,e[1]]):Ce&&ee(e=>[e[0],s])});q(()=>{A&&queueMicrotask(je)},[je,A]),q(()=>{A&&je()},[je,A,Ee]),q(()=>{if(!A)return;let e=T.current,t=fe.current;if(!e||!t)return;let n=R(e).ResizeObserver;if(typeof n!=`function`)return;let r=new n(je);return r.observe(e),r.observe(t),()=>{r.disconnect()}},[T,je,A]);let Me=se?`bottom`:`insetInlineStart`,Ne=se?`left`:`top`,Pe;oe?C===Se?Pe=2:Ae===Se&&(Pe=1):C===Se&&(Pe=1);let Fe;Fe=!A&&!Number.isFinite(Ee)?Ho:{position:`absolute`,[Me]:A?`var(--position)`:`${Ee}%`,[Ne]:`50%`,translate:`${(se||!ce?-1:1)*50}% ${(se?1:-1)*50}%`,zIndex:Pe,...A&&{"--position":`${De??0}%`,visibility:U&&ke||De===void 0?`hidden`:void 0}};let Ie;se&&(Ie=ce?`vertical-rl`:`vertical-lr`);let Le=typeof u==`function`?u(Se):o,Re=we({"aria-label":Le,"aria-labelledby":s??(Le==null?j:void 0),"aria-describedby":a,"aria-orientation":B,"aria-valuenow":Te,"aria-valuetext":typeof d==`function`?d(kf(Te,N,O),Te,Se):c??fp(re,Se,O,N),disabled:ae,form:L,id:ye,max:P,min:F,name:z,onChange(e){k(e.currentTarget.valueAsNumber,Se,e)},onFocus(e){let t=me.current;me.current=!1,W(Se),ue(!0),t&&e.stopPropagation()},onBlur(e){if(me.current){e.stopPropagation();return}W(-1),!ne.current.some(t=>Q(t,e.relatedTarget))&&(le(!0),ue(!1),de===`onBlur`&&D.commit(vf(Te,Se,F,P,oe,re)))},onKeyDown(e){if(e.defaultPrevented||!dp.has(e.key))return;Qf.has(e.key)&&e.stopPropagation();let t=null,n=0,r=e.shiftKey?M:G,i=Mf(Te,G,F);switch(e.key){case Gf:n=1;break;case Jf:n=ce?-1:1;break;case Kf:n=-1;break;case qf:n=ce?1:-1;break;case Xf:r=M,n=1;break;case Zf:r=M,n=-1;break;case`End`:t=oe&&Number.isFinite(re[Se+1])?re[Se+1]-G*I:P;break;case Yf:t=oe&&Number.isFinite(re[Se-1])?re[Se-1]+G*I:F}if(n!==0&&(t=pp(i,r,n,F,P)),t!==null){let n=e.currentTarget;ui(n)||(me.current=!0,n.blur(),n.focus({preventScroll:!0,focusVisible:!0})),k(t,Se,e),e.preventDefault()}},step:G,style:{...Ho,width:`100%`,height:`100%`,writingMode:Ie},tabIndex:y,type:`range`,value:Te??``},e=>D.getValidationProps(ae,e),{onFocus:he,onBlur:ge,onKeyDown:v}),ze=Je(pe,D.inputRef,m);return lt(`div`,e,{state:te,ref:[t,be,fe],props:[{"data-index":Se,children:(0,Z.jsxs)(_.Fragment,{children:[r,(0,Z.jsx)(`input`,{ref:ze,...Re,suppressHydrationWarning:!0}),A&&Ce&&U&&(up||=(0,Z.jsx)(lp,{script:``}))]}),id:S,onPointerDown(e){if(ae)return;H.current=Se;let t=Af(e.currentTarget,se);V.current=(se?e.clientY:e.clientX)-t},style:Fe,suppressHydrationWarning:U||void 0},x],stateAttributesMapping:xf})});function hp(e,t,n,r,i,a){let o={visibility:a||n&&(r===void 0||t&&i===void 0)?`hidden`:void 0,position:e?`absolute`:`relative`,[e?`width`:`height`]:`inherit`},s=`${r??0}%`,c=`${(i??0)-(r??0)}%`;return n&&(o[`--start-position`]=s,s=`var(--start-position)`,t&&(o[`--relative-size`]=c,c=`var(--relative-size)`)),o[e?`bottom`:`insetInlineStart`]=t?s:0,o[e?`height`:`width`]=t?c:s,o}var gp=_.forwardRef(function(e,t){let{render:n,className:r,style:i,...a}=e,{indicatorPosition:o,inset:s,max:c,min:l,orientation:u,renderBeforeHydration:d,state:f,values:p}=Cf(),m=Uf(),h=hp(u===`vertical`,p.length>1,s,s?o[0]:Wf(p[0],l,c),s?o[1]:Wf(p[p.length-1],l,c),s&&d&&m);return lt(`div`,e,{state:f,ref:t,props:[{"data-base-ui-slider-indicator":d?``:void 0,style:h,suppressHydrationWarning:d||void 0},a],stateAttributesMapping:xf})}),_p=340,vp=6;function yp(e){let[t,n]=_.useState(null),r=_.useCallback(()=>{n(null)},[]),i=_.useCallback((t,r)=>{t.defaultPrevented||e||t.button!==0||n(r)},[e]);return _.useEffect(()=>{if(t!==null)return window.addEventListener(`pointerup`,r),window.addEventListener(`pointercancel`,r),window.addEventListener(`blur`,r),()=>{window.removeEventListener(`pointerup`,r),window.removeEventListener(`pointercancel`,r),window.removeEventListener(`blur`,r)}},[t,r]),{activeDragIndex:t,handlePointerDown:i}}function bp({disabled:e=!1,isPointerDragging:t,markerCount:n,markerValues:r,max:i,min:a,orientation:o}){let s=r?.length?r.filter(e=>e>a&&e<i).map(e=>(e-a)/(i-a)*100):Array.from({length:n},(e,t)=>t===0||t===n-1?null:t/(n-1)*100).filter(e=>e!==null);return s.length===0?null:(0,Z.jsx)(Z.Fragment,{children:s.map((n,r)=>{let i=`${n}%`;return(0,Z.jsx)(`span`,{"aria-hidden":!0,className:X(`pointer-events-none absolute rounded-full bg-[color:var(--slider-active-color)] opacity-0 transition-opacity duration-150`,e?null:t?`opacity-100`:`group-hover/slider-control:opacity-100`,o===`vertical`?`left-1/2 h-px w-1.5 -translate-x-1/2 translate-y-1/2`:`top-1/2 h-1.5 w-px -translate-x-1/2 -translate-y-1/2`),"data-slot":`slider-marker`,style:o===`vertical`?{bottom:i}:{left:i}},`${i}-${r}`)})})}function xp({count:e,disabled:t=!1,getAriaLabel:n,onDoubleClick:r}){let{activeDragIndex:i,handlePointerDown:a}=yp(t),o=_.useRef(null),s=_.useRef(!1),c=_.useCallback((e,t)=>{if(e.detail>=2)return!0;let n=o.current;if(!n||n.index!==t)return!1;let r=e.timeStamp-n.timeStamp,i=e.clientX-n.clientX,a=e.clientY-n.clientY,s=Math.hypot(i,a);return n.pointerType===e.pointerType&&r>=0&&r<=_p&&s<=vp},[]),l=_.useCallback((e,n)=>{if(!(!r||t||e.button!==0)){if(c(e,n)){o.current=null,s.current=!0,r(e,n);return}o.current={clientX:e.clientX,clientY:e.clientY,index:n,pointerType:e.pointerType,timeStamp:e.timeStamp}}},[t,r,c]),u=_.useCallback((e,t)=>{if(s.current){s.current=!1,e.preventDefault(),e.stopPropagation();return}r?.(e,t)},[r]);return(0,Z.jsx)(Z.Fragment,{children:Array.from({length:e},(e,r)=>(0,Z.jsx)(mp,{"data-slot":`slider-thumb`,getAriaLabel:n,index:r,onDoubleClick:e=>u(e,r),onPointerDownCapture:e=>l(e,r),onPointerDown:e=>a(e,r),className:X(`group/slider-thumb relative block size-[9px] shrink-0 cursor-pointer rounded-[2px] select-none before:absolute before:top-1/2 before:left-1/2 before:block before:size-[18px] before:-translate-x-1/2 before:-translate-y-1/2 before:content-[''] transition-[inset-inline-start,bottom] duration-200 ease-out data-[dragging]:transition-none disabled:pointer-events-none motion-reduce:transition-none`),children:(0,Z.jsx)(`span`,{"aria-hidden":!0,"data-active-dragging":i===r?`true`:void 0,"data-slot":`slider-dot`,className:X(`pointer-events-none absolute inset-0 block rounded-[2px] bg-[color:var(--slider-active-color)] transition-[scale,background-color] duration-200 ease-out motion-reduce:transition-none`,t?null:`group-hover/slider-thumb:scale-[1.4] data-[active-dragging=true]:scale-[1.4]`)})},r))})}function Sp({show:e}){return e?(0,Z.jsx)(gp,{"data-slot":`slider-range`,className:X(`bg-[color:var(--slider-active-color)] transition-[width,height,inset-inline-start,bottom] duration-200 ease-out select-none data-[dragging]:transition-none data-horizontal:h-full data-vertical:w-full motion-reduce:transition-none`)}):null}function Cp({count:e,disabled:t,getAriaLabel:n,isDiscrete:r,isPointerDragging:i,markerCount:a,markerValues:o,max:s,min:c,onThumbDoubleClick:l,orientation:u,showFill:d}){return(0,Z.jsxs)(Rf,{className:`group/slider-control relative flex touch-none items-center select-none data-[disabled]:opacity-[0.15] data-horizontal:h-[18px] data-horizontal:w-full data-vertical:h-full data-vertical:min-h-40 data-vertical:w-[18px] data-vertical:flex-col`,children:[(0,Z.jsxs)(zf,{"data-slot":`slider-track`,className:`group/slider-track relative grow overflow-visible rounded-full bg-[color:var(--slider-track-color)] select-none data-horizontal:h-px data-horizontal:w-full data-vertical:h-full data-vertical:w-px`,children:[(0,Z.jsx)(Sp,{show:d}),r?(0,Z.jsx)(bp,{disabled:t,isPointerDragging:i,markerCount:a,markerValues:o,max:s,min:c,orientation:u}):null]}),(0,Z.jsx)(xp,{count:e,disabled:t,getAriaLabel:n,onDoubleClick:l})]})}var wp=_.createContext(null);function Tp(e){return typeof e==`number`?[e]:[...e]}function Ep(e,t){return e.length===t.length&&e.every((e,n)=>e===t[n])}function Dp({disabled:e,handleValueChange:t,max:n,min:r,values:i}){let a=_.useContext(wp),o=_.useRef(i);return _.useEffect(()=>{o.current=i},[i]),_.useCallback((i,s)=>{if(t(i,s),e)return;let c=o.current,l=Tp(i);Ep(c,l)||(a?.onValueChange?.({max:n,min:r,nextValues:l,previousValues:c}),o.current=l)},[e,t,n,r,a])}function Op({max:e,min:t,step:n}){if(!Number.isFinite(n)||!Number.isFinite(t)||!Number.isFinite(e)||n<=0||e<=t)return;let r=(e-t)/n,i=Math.round(r),a=Math.abs(r-i)<2**-52*100?i:Math.floor(r)+1;return Math.max(2,a+1)}function kp({markerCount:e,max:t,min:n,step:r,variant:i}){return i===`discrete`?e??Op({max:t,min:n,step:r})??Math.max(2,Math.round(t-n)+1):e??Math.max(2,Math.round(t-n)+1)}function Ap({disabled:e,onBlurCapture:t,onPointerCancelCapture:n,onPointerDownCapture:r,onPointerUpCapture:i}){let[a,o]=_.useState(!1),s=_.useCallback(()=>{o(!1)},[]),c=_.useCallback(t=>{r?.(t),!(t.defaultPrevented||e||t.button!==0)&&o(!0)},[e,r]),l=_.useCallback(e=>{i?.(e),s()},[i,s]),u=_.useCallback(e=>{n?.(e),s()},[n,s]),d=_.useCallback(e=>{t?.(e),s()},[t,s]);return _.useEffect(()=>{if(a)return window.addEventListener(`pointerup`,s),window.addEventListener(`pointercancel`,s),window.addEventListener(`blur`,s),()=>{window.removeEventListener(`pointerup`,s),window.removeEventListener(`pointercancel`,s),window.removeEventListener(`blur`,s)}},[a,s]),{handleBlurCapture:d,handlePointerCancelCapture:u,handlePointerDownCapture:c,handlePointerUpCapture:l,isPointerDragging:a}}function jp(e,t,n,r){let i=r>0?r:1,a=t+Math.round((e-t)/i)*i;return Math.min(n,Math.max(t,Number(a.toFixed(6))))}function Mp(e,t,n,r){if(!r?.length)return null;let i=r.filter(e=>Number.isFinite(e)).map(e=>Math.min(n,Math.max(t,e)));if(!i.length)return null;let a=i.reduce((t,n)=>{let r=Math.abs(t-e);return Math.abs(n-e)<r?n:t},i[0]);return Number(a.toFixed(6))}function Np(e,t,n,r){return Array.isArray(e)?[...e]:typeof e==`number`?[e]:Array.isArray(t)?[...t]:typeof t==`number`?[t]:[n,r]}function Pp(e,t,n,r){let i=t??n;return Array.isArray(i)?Array.isArray(e)?[...e]:[e]:typeof i==`number`&&Array.isArray(e)?e[0]??r:e}function Fp(e,t,n,r,i){if(typeof e==`number`){let a=Mp(e,t,n,i);return a===null?jp(e,t,n,r):a}return e.map(e=>Mp(e,t,n,i)??jp(e,t,n,r))}function Ip(e,t){return Array.isArray(e)&&Array.isArray(t)?e.length===t.length&&e.every((e,n)=>e===t[n]):e===t}function Lp(e,t){return{activeThumbIndex:t,allowPropagation:()=>void 0,cancel:()=>void 0,event:e.nativeEvent,isCanceled:!1,isPropagationAllowed:!1,reason:`none`,trigger:e.currentTarget}}function Rp(e){return{event:e.nativeEvent,reason:`none`}}function zp(e,t,n){if(!Array.isArray(e)||!Array.isArray(t))return t;let r=[...e],i=t[n]??e[n];return i===void 0?e:(r[n]=i,r)}function Bp({defaultValue:e,disabled:t,handleValueChange:n,handleValueCommitted:r,isDiscrete:i,max:a,min:o,resetValue:s,snapValues:c,step:l,value:u,values:d}){let f=_.useRef(s??e??u);return _.useCallback((p,m)=>{if(t)return;let h=s??e??f.current;if(h===void 0)return;p.preventDefault(),p.stopPropagation();let g=Pp(h,u,e,o),_=Pp(d,u,e,o),v=zp(_,g,m),y=i?Fp(v,o,a,l,c):v;Ip(_,y)||(n?.(y,Lp(p,m)),r(y,Rp(p)))},[e,t,n,r,i,a,o,s,c,l,u,d])}function Vp({discreteValue:e,isDiscrete:t,lastInternalDiscreteValueRef:n,max:r,min:i,setDiscreteValue:a,snapValues:o,step:s,value:c}){_.useEffect(()=>{if(!t||c===void 0||e===void 0)return;let l=n.current;l!==void 0&&(Ip(c,l)||Ip(c,Fp(l,i,r,s,o)))||a(void 0)},[e,t,n,r,i,a,o,s,c])}function Hp({defaultValue:e,largeStep:t,max:n,min:r,onValueChange:i,onValueCommitted:a,snapValues:o,step:s,value:c,variant:l}){let[u,d]=_.useState(()=>c===void 0?e:void 0),f=_.useRef(c===void 0?e:void 0),p=_.useRef(null),m=l===`discrete`,h=m?u??c??e:c,g=m?Math.max((n-r)/1e3,1e-6):s,v=m?t??s:t,y=_.useMemo(()=>Np(h,e,r,n),[h,e,r,n]);return Vp({discreteValue:u,isDiscrete:m,lastInternalDiscreteValueRef:f,max:n,min:r,setDiscreteValue:d,snapValues:o,step:s,value:c}),{handleValueChange:_.useCallback((t,a)=>{if(p.current=a,m){let l=Pp(t,c,e,r);f.current=l,d(l),i?.(Fp(l,r,n,s,o),a);return}i?.(t,a)},[e,m,n,r,i,o,s,c]),handleValueCommitted:_.useCallback((t,l)=>{if(!m){a?.(t,l);return}let u=Pp(t,c,e,r),h=Fp(u,r,n,s,o);f.current=h,d(h),!Ip(h,u)&&p.current&&i?.(h,p.current),a?.(h,l)},[e,m,n,r,i,a,o,s,c]),isDiscrete:m,resolvedValue:h,rootLargeStep:v,rootStep:g,values:y}}function Up({defaultValue:e,disabled:t,largeStep:n,markerCount:r,max:i,min:a,onBlurCapture:o,onPointerCancelCapture:s,onPointerDownCapture:c,onPointerUpCapture:l,onValueChange:u,onValueCommitted:d,resetValue:f,snapValues:p,step:m,value:h,variant:g}){let _=Hp({defaultValue:e,largeStep:n,max:i,min:a,onValueChange:u,onValueCommitted:d,snapValues:p,step:m,value:h,variant:g}),v=Ap({disabled:t,onBlurCapture:o,onPointerCancelCapture:s,onPointerDownCapture:c,onPointerUpCapture:l}),y=kp({markerCount:r,max:i,min:a,step:m,variant:g}),b=Dp({disabled:t,handleValueChange:_.handleValueChange,max:i,min:a,values:_.values});return{handleThumbDoubleClick:Bp({defaultValue:e,disabled:t,handleValueChange:b,handleValueCommitted:_.handleValueCommitted,isDiscrete:_.isDiscrete,max:i,min:a,resetValue:f,snapValues:p,step:m,value:h,values:_.values}),handleValueChange:b,pointerDrag:v,resolvedMarkerCount:y,sliderValue:_}}function Wp({className:e,defaultValue:t,disabled:n,getAriaLabel:r,largeStep:i,markerCount:a,markerValues:o,onBlurCapture:s,onPointerCancelCapture:c,onPointerDownCapture:l,onPointerUpCapture:u,onValueChange:d,onValueCommitted:f,orientation:p=`horizontal`,resetValue:m,showFill:h=!0,snapValues:g,step:_=1,thumbAlignment:v=`edge`,variant:y=`continuous`,value:b,min:x=0,max:S=100,...C}){let{handleThumbDoubleClick:w,handleValueChange:T,pointerDrag:E,resolvedMarkerCount:D,sliderValue:O}=Up({defaultValue:t,disabled:n,largeStep:i,markerCount:a,max:S,min:x,onBlurCapture:s,onPointerCancelCapture:c,onPointerDownCapture:l,onPointerUpCapture:u,onValueChange:d,onValueCommitted:f,resetValue:m,snapValues:g,step:_,value:b,variant:y});return(0,Z.jsx)(Tf,{className:X(`app-no-drag data-horizontal:w-full data-vertical:h-full`,`[--slider-active-color:var(--foreground)] [--slider-track-color:color-mix(in_oklab,var(--muted-foreground)_38%,transparent)]`,`data-[disabled]:[--slider-active-color:var(--foreground)] data-[disabled]:[--slider-track-color:var(--foreground)]`,e),"data-slot":`slider`,"data-variant":y,defaultValue:O.isDiscrete?void 0:t,value:O.resolvedValue,min:x,max:S,disabled:n,largeStep:O.rootLargeStep,onBlurCapture:E.handleBlurCapture,onPointerCancelCapture:E.handlePointerCancelCapture,onPointerDownCapture:E.handlePointerDownCapture,onPointerUpCapture:E.handlePointerUpCapture,onValueChange:T,onValueCommitted:O.handleValueCommitted,orientation:p,step:O.rootStep,thumbAlignment:v,thumbCollisionBehavior:`none`,...C,children:(0,Z.jsx)(Cp,{count:O.values.length,disabled:n,getAriaLabel:r,isDiscrete:O.isDiscrete,isPointerDragging:E.isPointerDragging,markerCount:D,markerValues:o,max:S,min:x,onThumbDoubleClick:w,orientation:p,showFill:h})})}var Gp=`block h-full min-w-0 overflow-hidden whitespace-nowrap font-sans text-xs leading-5 tabular-nums`,Kp=`inline-grid h-5 shrink-0`;function qp({ariaLabel:e,disabled:t=!1,editAriaLabel:n,layout:r=`reference`,maxValueLabel:i,onCommit:a,onStep:o,textAlign:s=`right`,valueLabel:c}){let[l,u]=(0,_.useState)(!1),d=(0,_.useRef)(null),f=(0,_.useRef)(c),p=im(c),m=Xp({layout:r,textAlign:s}),h=rm(c,i);if((0,_.useEffect)(()=>{f.current=c},[c]),(0,_.useEffect)(()=>{if(l){let e=d.current;if(!e)return;e.textContent=f.current,e.focus(),am(e)}},[l]),t||!a||!p){let e=t?`text-[color:color-mix(in_oklab,var(--foreground)_60%,transparent)] opacity-60`:`text-[color:var(--muted-foreground)]`;return(0,Z.jsxs)(`span`,{className:Yp(r,`cursor-default`),children:[r===`reference`?(0,Z.jsx)(Jp,{valueLabel:h}):null,(0,Z.jsx)(`span`,{className:`col-start-1 row-start-1 cursor-default ${e} ${m}`,children:c})]})}function g(){a?.(d.current?.textContent??f.current),u(!1)}return(0,Z.jsxs)(`span`,{className:Yp(r),children:[r===`reference`?(0,Z.jsx)(Jp,{valueLabel:h}):null,l?(0,Z.jsx)(Zp,{ariaLabel:e,editorRef:d,layout:r,onCancel:()=>u(!1),onCommit:g,onStep:o,textClassName:m}):(0,Z.jsx)(Qp,{ariaLabel:n??`编辑${e}`,layout:r,onBeginEditing:()=>u(!0),textClassName:m,valueLabel:c})]})}function Jp({valueLabel:e}){return(0,Z.jsx)(`span`,{"aria-hidden":`true`,className:`invisible col-start-1 row-start-1 min-w-[4ch] pointer-events-none text-[color:var(--muted-foreground)] ${Xp({layout:`reference`,textAlign:`right`})}`,"data-slider-value-label-measure":``,children:e})}function Yp(e,t=``){return[Kp,e===`content`?`w-fit justify-items-start`:`place-items-center`,t].filter(Boolean).join(` `)}function Xp({layout:e,textAlign:t}){return[Gp,e===`content`?`w-auto`:`w-full`,t===`left`?`text-left`:`text-right`].join(` `)}function Zp({ariaLabel:e,editorRef:t,layout:n,onCancel:r,onCommit:i,onStep:a,textClassName:o}){return(0,Z.jsx)(`span`,{"aria-label":e,className:`col-start-1 row-start-1 cursor-text p-0 text-[color:var(--foreground)] outline-none ${n===`content`?`justify-self-start`:``} ${o}`,contentEditable:!0,onBlur:i,onFocus:e=>am(e.currentTarget),onKeyDown:e=>{if(e.key===`Enter`&&(e.preventDefault(),i()),e.key===`Escape`&&(e.preventDefault(),r()),e.key===`ArrowUp`||e.key===`ArrowDown`){let t=a?.(e.key===`ArrowUp`?1:-1,e.currentTarget.textContent??``);typeof t==`string`&&(e.preventDefault(),e.currentTarget.textContent=t,am(e.currentTarget))}},onPointerDown:e=>e.stopPropagation(),ref:t,role:`textbox`,suppressContentEditableWarning:!0,tabIndex:0})}function Qp({ariaLabel:e,layout:t,onBeginEditing:n,textClassName:r,valueLabel:i}){function a(e){e.stopPropagation(),n()}return(0,Z.jsx)(`button`,{"aria-label":e,className:`col-start-1 row-start-1 h-full min-w-0 appearance-none cursor-text border-0 bg-transparent p-0 transition-colors ${t===`content`?`w-auto justify-self-start`:`w-full`}`,onClick:a,onKeyDown:e=>{(e.key===`Enter`||e.key===` `)&&(e.preventDefault(),e.stopPropagation(),n())},onMouseDown:$p,onMouseUp:a,onPointerDown:$p,onPointerUp:a,type:`button`,children:(0,Z.jsx)(`span`,{className:`cursor-text text-[color:var(--muted-foreground)] transition-colors duration-200 ease-out hover:text-[color:var(--foreground)] ${r}`,children:i})})}function $p(e){e.stopPropagation()}function em(e,{max:t=100,min:n=0}){let r=Array.from(e.matchAll(/-?\d+(?:\.\d+)?/g));if(r.length===0)return;let i=Math.max(...r.map(tm)),a=[n,t].map(e=>nm(e,i)).sort((e,t)=>t.length-e.length)[0];return e.replaceAll(/-?\d+(?:\.\d+)?/g,a??``)}function tm(e){return e[0].split(`.`)[1]?.length??0}function nm(e,t){return t>0?e.toFixed(t):`${Math.round(e)}`}function rm(e,t){return!t||e.length>t.length?e:t}function im(e){return/-?\d+(?:\.\d+)?/.test(e)}function am(e){let t=window.getSelection();if(!t)return;let n=document.createRange();n.selectNodeContents(e),t.removeAllRanges(),t.addRange(n)}var om=mo,sm=xt(X(`flex field-sizing-content resize-none`,ho),{variants:{size:{content:`min-h-0 px-2 py-2 text-sm/relaxed`,sm:`min-h-14 px-2 py-1.5 text-xs/relaxed`,default:`min-h-16 px-2 py-2 text-xs-plus/relaxed`,lg:`min-h-20 px-2.5 py-2.5 text-sm/relaxed`,xl:`min-h-24 px-3 py-3 text-base/relaxed`},variant:{default:``,"code-editor":`relative z-10 min-h-0 overflow-x-auto overflow-y-hidden font-mono whitespace-pre text-xs/relaxed text-transparent caret-[color:var(--foreground)] selection:bg-[color:var(--accent)] selection:text-transparent`}},defaultVariants:{size:`default`,variant:`default`}}),cm=_.forwardRef(function({className:e,size:t,variant:n,...r},i){return(0,Z.jsx)(`textarea`,{ref:i,"data-size":t??`default`,"data-slot":`textarea`,"data-variant":n??`default`,className:X(sm({size:t,variant:n}),e),...r})}),lm=_.createContext(`default`);function um(){return _.useContext(lm)}var dm=xt(X(`group/input-group relative flex w-full min-w-0 items-center rounded-lg border border-[color:color-mix(in_oklab,var(--border)_12%,transparent)] transition-colors outline-none in-data-[slot=combobox-content]:focus-within:border-inherit in-data-[slot=combobox-content]:focus-within:ring-0 has-data-[align=block-end]:rounded-lg has-data-[align=block-start]:rounded-lg has-[[data-slot][aria-invalid=true]]:border-[color:var(--destructive)] has-[textarea]:rounded-lg has-[>[data-align=block-end]]:h-auto has-[>[data-align=block-end]]:flex-col has-[>[data-align=block-start]]:h-auto has-[>[data-align=block-start]]:flex-col has-[>textarea]:h-auto has-[>[data-align=block-end]]:[&>input]:pt-3 has-[>[data-align=block-start]]:[&>input]:pb-3 has-[>[data-align=inline-end]]:[&>input]:pr-1.5 has-[>[data-align=inline-start]]:[&>input]:pl-1.5`,`[&:not(:focus-within):hover]:!border-[color:color-mix(in_oklab,var(--border)_20%,transparent)] [&:not(:focus-within):hover]:text-[color:var(--foreground)]`),{variants:{size:{sm:`h-6`,default:`h-7`,lg:`h-8`,xl:`h-10`},surfaceStyle:{default:om,transparent:`bg-transparent dark:bg-transparent`,"toolbar-address":``},focusStyle:{default:`has-[[data-slot=input-group-control]:focus]:border-[color:color-mix(in_oklab,var(--border)_30%,transparent)] in-data-[slot=combobox-content]:has-[[data-slot=input-group-control]:focus]:border-inherit`,none:``,"toolbar-address":``}},defaultVariants:{size:`default`,surfaceStyle:`default`,focusStyle:`default`}});function fm({className:e,surfaceStyle:t,focusStyle:n,size:r=`default`,...i}){let a=r??`default`;return(0,Z.jsx)(lm.Provider,{value:a,children:(0,Z.jsx)(`div`,{"data-focus-style":n??void 0,"data-size":a,"data-slot":`input-group`,"data-surface-style":t??void 0,role:`group`,className:X(dm({focusStyle:n,size:a,surfaceStyle:t}),e),...i})})}var pm=xt(`flex h-auto cursor-text items-center justify-center gap-1 py-2 font-medium text-[color:var(--muted-foreground)] select-none group-data-[disabled=true]/input-group:opacity-50 [&>svg]:text-[color:var(--foreground)] **:data-[slot=kbd]:rounded-[calc(var(--radius-sm)-2px)] **:data-[slot=kbd]:bg-[color:color-mix(in_oklab,var(--muted-foreground)_10%,transparent)] **:data-[slot=kbd]:px-1 **:data-[slot=kbd]:text-[0.625rem] [&>svg:not([class*='size-'])]:size-3.5`,{variants:{align:{"inline-start":`order-first pl-2 has-[>button]:pl-px has-[>kbd]:ml-[-0.275rem]`,"inline-end":`order-last pr-1.5 has-[>button]:pr-0.5 has-[>kbd]:mr-[-0.275rem]`,"block-start":`order-first w-full justify-start px-2 pt-2 group-has-[>input]/input-group:pt-2 [.border-b]:pb-2`,"block-end":`order-last w-full justify-start px-2 pb-2 group-has-[>input]/input-group:pb-2 [.border-t]:pt-2`},size:{sm:`text-xs/relaxed`,default:`text-xs/relaxed`,lg:`gap-1.5 text-sm/relaxed data-[align=inline-start]:pl-2.5 data-[align=inline-start]:has-[>button]:pl-px data-[align=inline-end]:pr-2 data-[align=inline-end]:has-[>button]:pr-0.5 data-[align=block-start]:px-2.5 data-[align=block-end]:px-2.5 [&>svg:not([class*='size-'])]:size-4`,xl:`gap-2 text-base/relaxed data-[align=inline-start]:pl-3 data-[align=inline-start]:has-[>button]:pl-px data-[align=inline-end]:pr-2.5 data-[align=inline-end]:has-[>button]:pr-0.5 data-[align=block-start]:px-3 data-[align=block-end]:px-3 [&>svg:not([class*='size-'])]:size-4`}},defaultVariants:{align:`inline-start`,size:`default`}});function mm({className:e,align:t=`inline-start`,...n}){let r=um();return(0,Z.jsx)(`div`,{role:`group`,"data-slot":`input-group-addon`,"data-align":t,className:X(pm({align:t,size:r}),e),onMouseDown:e=>{e.target.closest(`button`)||(e.preventDefault(),e.currentTarget.parentElement?.querySelector(`input`)?.focus())},...n})}var hm=xt(`flex items-center gap-2 text-[color:color-mix(in_oklab,var(--foreground)_40%,transparent)] group-hover/input-group:text-[color:var(--foreground)] group-has-[[data-slot=input-group-control]:focus]/input-group:text-[color:var(--foreground)] [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4`,{variants:{size:{sm:`text-xs/relaxed`,default:`text-xs/relaxed`,lg:`text-sm/relaxed [&_svg:not([class*='size-'])]:size-4`,xl:`text-base/relaxed [&_svg:not([class*='size-'])]:size-4`}},defaultVariants:{size:`default`}});function gm({className:e,...t}){let n=um();return(0,Z.jsx)(`span`,{"data-slot":`input-group-text`,className:X(hm({size:n}),e),...t})}var _m=xt(`h-full flex-1 border-0 shadow-none ring-0 focus-visible:ring-0 aria-invalid:ring-0`,{variants:{size:{sm:`px-2 py-0 text-xs/relaxed`,default:`px-2 py-0.5 text-xs/relaxed`,lg:`px-2.5 py-1 text-sm/relaxed`,xl:`px-3 py-1.5 text-base/relaxed`},surfaceStyle:{default:`rounded-none bg-transparent dark:bg-transparent`,hoverInput:`rounded-lg bg-transparent hover:bg-[color:color-mix(in_oklab,var(--input)_30%,transparent)] dark:bg-transparent dark:hover:bg-[color:color-mix(in_oklab,var(--input)_30%,transparent)]`,"toolbar-address":`rounded-none bg-transparent dark:bg-transparent`},typographyStyle:{default:``,addressBar:`text-xs-plus tracking-normal font-normal md:text-xs-plus`,popup:`popup-text-xs-plus leading-normal tracking-tight font-normal`}},defaultVariants:{size:`default`,surfaceStyle:`default`,typographyStyle:`default`}});function vm({className:e,surfaceStyle:t,typographyStyle:n,...r}){let i=um();return(0,Z.jsx)(vo,{"data-surface-style":t??void 0,"data-typography-style":n??void 0,"data-slot":`input-group-control`,className:X(_m({size:i,surfaceStyle:t,typographyStyle:n}),e),...r})}_.forwardRef(function({className:e,...t},n){let r=um();return(0,Z.jsx)(cm,{ref:n,"data-slot":`input-group-control`,className:X(`flex-1 resize-none rounded-none border-0 bg-transparent shadow-none ring-0 focus-visible:ring-0 aria-invalid:ring-0 dark:bg-transparent`,e),size:r,...t})});var ym=_.createContext(void 0);function bm(e){let t=_.useContext(ym);if(t===void 0&&!e)throw Error(ze(47));return t}var xm={...Ol,disabled:e=>e.disabled,instantType:e=>e.instantType,openMethod:e=>e.openMethod,openChangeReason:e=>e.openChangeReason,modal:e=>e.modal,focusManagerModal:e=>e.focusManagerModal,stickIfOpen:e=>e.stickIfOpen,titleElementId:e=>e.titleElementId,descriptionElementId:e=>e.descriptionElementId,openOnHover:e=>e.openOnHover,closeDelay:e=>e.closeDelay,adaptiveOrigin:e=>e.adaptiveOrigin},Sm=class extends nl{constructor(e,t,n){let r=new yl;super(Cm(e,r,t,n),wm(r),xm)}setOpen=(e,t)=>{let n=t.reason===Ka,r=t.reason===`trigger-press`&&t.event.detail===0,i=!e&&(t.reason===`escape-key`||t.reason==null),a=fl(t),o=this.select(`activeTriggerId`);if(!e&&t.reason===`close-press`&&t.trigger==null&&o!=null&&(t.trigger=this.context.triggerElements.getById(o)??this.select(`activeTriggerElement`)??void 0),this.context.onOpenChange?.(e,t),t.isCanceled)return;this.state.floatingRootContext.dispatchOpenChange(e,t);let s=()=>{let n={open:e,openChangeReason:t.reason};dl(n,e,t.trigger,a()),this.update(n)};n?(this.set(`stickIfOpen`,!0),this.context.stickIfOpenTimeout.start(500,()=>{this.set(`stickIfOpen`,!1)}),Pa.flushSync(s)):s();let c;r?c=`click`:i?c=`dismiss`:t.reason===`focus-out`&&(c=`focus`),this.set(`instantType`,c)}};function Cm(e,t,n,r=!1){let i={...xl(),disabled:!1,modal:!1,focusManagerModal:!1,instantType:void 0,openMethod:null,openChangeReason:null,titleElementId:void 0,descriptionElementId:void 0,stickIfOpen:!0,openOnHover:!1,closeDelay:0,adaptiveOrigin:void 0,...e};return i.open&&e?.mounted===void 0&&(i.mounted=!0),i.floatingRootContext=Sl(t,n,r),i}function wm(e){return{popupRef:_.createRef(),onOpenChange:void 0,onOpenChangeComplete:void 0,triggerFocusTargetRef:_.createRef(),beforeContentFocusGuardRef:_.createRef(),stickIfOpenTimeout:new Da,triggerElements:e}}function Tm({props:e}){let{children:t,open:n,defaultOpen:r=!1,onOpenChange:i,onOpenChangeComplete:a,modal:o=!1,handle:s,triggerId:c,defaultTriggerId:l=null}=e,u=Dm(s,{modal:o,open:r,openProp:n,activeTriggerId:l,triggerIdProp:c});u.useControlledProp(`openProp`,n),u.useControlledProp(`triggerIdProp`,c);let d=u.useState(`open`),f=u.useState(`mounted`),p=u.useState(`payload`);u.useContextCallback(`onOpenChange`,i),u.useContextCallback(`onOpenChangeComplete`,a),vl(u,d),hl(u);let{forceUnmount:m}=gl(d,u,()=>{u.update({stickIfOpen:!0,openChangeReason:null})});u.useSyncedValues({modal:o}),_.useEffect(()=>{d||u.context.stickIfOpenTimeout.clear()},[u,d]),_.useImperativeHandle(e.actionsRef,()=>({unmount:m,close:()=>u.setOpen(!1,$(co))}),[m,u]);let h=d||f;return(0,Z.jsxs)(ym.Provider,{value:u,children:[s&&(0,Z.jsx)(ll,{handle:s,store:u}),h&&(0,Z.jsx)(Om,{store:u,modal:o}),typeof t==`function`?t({payload:p}):t]})}function Em(e){return bm(!0)?(0,Z.jsx)(Tm,{props:e}):(0,Z.jsx)(ws,{children:(0,Z.jsx)(Tm,{props:e})})}function Dm(e,t){let n=cl((e,n)=>new Sm(t,e,n));return _.useEffect(()=>n.context.stickIfOpenTimeout.disposeEffect(),[n]),n}function Om({store:e,modal:t}){let n=Bs(e.useState(`floatingRootContext`),{outsidePressEvent:{mouse:t===`trap-focus`?`sloppy`:`intentional`,touch:`sloppy`}}),r=n.reference,i=n.floating;return _l(e,{activeTriggerProps:r,inactiveTriggerProps:r,popupProps:i}),null}function km(e,t){let n=_.useRef(null);function r(t){Pa.flushSync(()=>{e.setOpen(!1,$($a,t.nativeEvent,t.currentTarget))}),xa(n.current)?.focus()}function i(n){let r=e.select(`positionerElement`);if(r&&Sa(n,r))e.context.beforeContentFocusGuardRef.current?.focus();else{Pa.flushSync(()=>{e.setOpen(!1,$($a,n.nativeEvent,n.currentTarget))});let i=ba(e.context.triggerFocusTargetRef.current||t.current);for(;i!==null&&Q(r,i);){let e=i;if(i=_a(i),i===e)break}i?.focus()}}return{preFocusGuardRef:n,handlePreFocusGuardFocus:r,handleFocusTargetFocus:i}}function Am(e){let t=_.useRef(``),n=_.useCallback(n=>{n.defaultPrevented||(t.current=n.pointerType,e(n,n.pointerType))},[e]);return{onClick:_.useCallback(n=>{if(n.detail===0){e(n,`keyboard`);return}`pointerType`in n?e(n,n.pointerType):e(n,t.current),t.current=``},[e]),onPointerDown:n}}function jm(e,t){let{onClick:n,onPointerDown:r}=Am(K((n,r)=>{(typeof e==`function`?e():e)||t(r||(Hr?`touch`:``))}));return _.useMemo(()=>({onClick:n,onPointerDown:r}),[n,r])}function Mm(e){let[t,n]=_.useState(null),r=jm(e,n);return Kd(e,t=>{t&&!e&&n(null)}),_.useMemo(()=>({openMethod:t,triggerProps:r}),[t,r])}var Nm=_.forwardRef(function(e,t){let{render:n,className:r,style:i,disabled:a=!1,nativeButton:o=!0,handle:s,payload:c,openOnHover:l=!1,delay:u=300,closeDelay:d=0,id:f,...p}=e,m=bm(!0),h=kl(s)??m;if(!h)throw Error(ze(74));let g=kr(f),v=h.useState(`isTriggerActive`,g),y=h.useState(`floatingRootContext`),b=h.useState(`isOpenedByTrigger`,g),x=h.useState(`triggerPopupId`,g),S=_.useRef(null),{registerTrigger:C,isMountedByThisTrigger:w}=ml(g,S,h,{payload:c,disabled:a,openOnHover:l,closeDelay:d}),T=h.useState(`openChangeReason`),E=h.useState(`stickIfOpen`),D=h.useState(`openMethod`),O=h.useState(`focusManagerModal`),k=Hl(y,{enabled:!a&&l&&(D!==`touch`||T!==`trigger-press`),mouseOnly:!0,move:!1,handleClose:au(),restMs:u,delay:{close:d},triggerElementRef:S,isActiveTrigger:v,isClosing:()=>h.select(`transitionStatus`)===`ending`}),A=Ps(y,{stickIfOpen:E}),j=jm(()=>h.select(`open`),e=>{h.set(`openMethod`,e)}),M=h.useState(`triggerProps`,w),{getButtonProps:N,buttonRef:P}=Ge({disabled:a,native:o}),F={open(e){return e&&T===`trigger-press`?vu.open(e):_u.open(e)}},{preFocusGuardRef:I,handlePreFocusGuardFocus:L,handleFocusTargetFocus:R}=km(h,S),z=lt(`button`,e,{state:{disabled:a,open:b},ref:[P,t,C,S],props:[A.reference,k,M,j,{[ss]:``,id:g,"aria-haspopup":`dialog`,"aria-expanded":b,"aria-controls":x},p,N],stateAttributesMapping:F}),B=(0,Z.jsx)(_.Fragment,{children:z},g);return w&&!O?(0,Z.jsxs)(_.Fragment,{children:[(0,Z.jsx)(Wo,{ref:I,onFocus:L}),B,(0,Z.jsx)(Wo,{ref:h.context.triggerFocusTargetRef,onFocus:R})]}):B}),Pm=_.createContext(void 0);function Fm(){let e=_.useContext(Pm);if(e===void 0)throw Error(ze(45));return e}var Im=_.forwardRef(function(e,t){let{keepMounted:n=!1,...r}=e;return bm().useState(`mounted`)||n?(0,Z.jsx)(Pm.Provider,{value:n,children:(0,Z.jsx)(hs,{ref:t,...r})}):null}),Lm=_.createContext(void 0);function Rm(){let e=_.useContext(Lm);if(!e)throw Error(ze(46));return e}var zm=_.forwardRef(function(e,t){let{cutout:n,...r}=e,i;if(n){let e=n.getBoundingClientRect();i=`polygon(0% 0%,100% 0%,100% 100%,0% 100%,0% 0%,${e.left}px ${e.top}px,${e.left}px ${e.bottom}px,${e.right}px ${e.bottom}px,${e.right}px ${e.top}px,${e.left}px ${e.top}px)`}return(0,Z.jsx)(`div`,{ref:t,role:`presentation`,"data-base-ui-inert":``,...r,style:{position:`fixed`,inset:0,userSelect:`none`,WebkitUserSelect:`none`,clipPath:i}})}),Bm={},Vm={},Hm=``;function Um(e,t){return W(e)?e:t}function Wm(e,t,n){return/hidden|clip/.test(e.getComputedStyle(Um(t,n)).overflowY)}function Gm(e){if(typeof document>`u`)return!1;let t=Ue(e);return R(t).innerWidth-t.documentElement.clientWidth>0}function Km(e){if(!(typeof CSS<`u`&&CSS.supports&&CSS.supports(`scrollbar-gutter`,`stable`))||typeof document>`u`)return!1;let t=Ue(e),n=t.documentElement,r=t.body,i=Um(n,r),a=i.style.overflowY,o=n.style.scrollbarGutter;n.style.scrollbarGutter=`stable`,i.style.overflowY=`scroll`;let s=i.offsetWidth;i.style.overflowY=`hidden`;let c=i.offsetWidth;return i.style.overflowY=a,n.style.scrollbarGutter=o,s===c}function qm(e){let t=Ue(e),n=t.documentElement,r=t.body,i=Um(n,r),a={overflowY:i.style.overflowY,overflowX:i.style.overflowX};return Object.assign(i.style,{overflowY:`hidden`,overflowX:`hidden`}),()=>{Object.assign(i.style,a)}}function Jm(e){let t=Ue(e),n=t.documentElement,r=t.body,i=R(n),a=0,o=0,s=!1,c=ja.create();if(qr&&(i.visualViewport?.scale??1)!==1)return()=>{};function l(){let t=i.getComputedStyle(n),c=i.getComputedStyle(r),l=(t.scrollbarGutter||``).includes(`both-edges`)?`stable both-edges`:`stable`;a=n.scrollTop,o=n.scrollLeft,Bm={scrollbarGutter:n.style.scrollbarGutter,overflowY:n.style.overflowY,overflowX:n.style.overflowX},Hm=n.style.scrollBehavior,Vm={position:r.style.position,height:r.style.height,width:r.style.width,boxSizing:r.style.boxSizing,overflowY:r.style.overflowY,overflowX:r.style.overflowX,scrollBehavior:r.style.scrollBehavior};let u=n.scrollHeight>n.clientHeight,d=n.scrollWidth>n.clientWidth,f=t.overflowY===`scroll`||c.overflowY===`scroll`,p=t.overflowX===`scroll`||c.overflowX===`scroll`,m=Math.max(0,i.innerWidth-r.clientWidth),h=Math.max(0,i.innerHeight-r.clientHeight),g=parseFloat(c.marginTop)+parseFloat(c.marginBottom),_=parseFloat(c.marginLeft)+parseFloat(c.marginRight),v=Um(n,r);if(s=Km(e),s){n.style.scrollbarGutter=l,v.style.overflowY=`hidden`,v.style.overflowX=`hidden`;return}Object.assign(n.style,{scrollbarGutter:l,overflowY:`hidden`,overflowX:`hidden`}),(u||f)&&(n.style.overflowY=`scroll`),(d||p)&&(n.style.overflowX=`scroll`),Object.assign(r.style,{position:`relative`,height:g||h?`calc(100dvh - ${g+h}px)`:`100dvh`,width:_||m?`calc(100vw - ${_+m}px)`:`100vw`,boxSizing:`border-box`,overflowY:`hidden`,overflowX:`hidden`,scrollBehavior:`unset`}),r.scrollTop=a,r.scrollLeft=o,n.setAttribute(`data-base-ui-scroll-locked`,``),n.style.scrollBehavior=`unset`}function u(){Object.assign(n.style,Bm),Object.assign(r.style,Vm),s||(n.scrollTop=a,n.scrollLeft=o,n.removeAttribute(`data-base-ui-scroll-locked`),n.style.scrollBehavior=Hm)}function d(){u(),c.request(l)}l();let f=Lo(i,`resize`,d);return()=>{c.cancel(),u(),typeof i.removeEventListener==`function`&&f()}}var Ym=new class{lockCount=0;restore=null;timeoutLock=Da.create();timeoutUnlock=Da.create();acquire(e){return this.lockCount+=1,this.lockCount===1&&this.restore===null&&this.timeoutLock.start(0,()=>this.lock(e)),this.release}release=()=>{--this.lockCount,this.lockCount===0&&this.restore&&this.timeoutUnlock.start(0,this.unlock)};unlock=()=>{this.lockCount===0&&this.restore&&(this.restore?.(),this.restore=null)};lock(e){if(this.lockCount===0||this.restore!==null)return;let t=Ue(e),n=t.documentElement,r=t.body,i=R(n);if(Wm(i,n,r)){let t=new i.MutationObserver(()=>{Wm(i,n,r)||(t.disconnect(),this.restore=null,this.lock(e))}),a={attributes:!0};t.observe(n,a),t.observe(r,a),this.restore=()=>t.disconnect();return}let a=Hr||!Gm(e);this.restore=a?qm(e):Jm(e)}};function Xm(e=!0,t=null){q(()=>{if(e)return Ym.acquire(t)},[e,t])}var Zm=20;function Qm(e,t,n,r){let[i,a]=_.useState(!1);q(()=>{if(!e||!t||n==null){a(!1);return}let r=Ue(n).documentElement.clientWidth,i=n.offsetWidth;a(r>0&&i>0&&i>=r-Zm)},[e,t,n]),Xm(e&&(!t||i),r)}var $m=_.forwardRef(function(e,t){let{render:n,className:r,style:i,anchor:a,positionMethod:o,side:s,align:c,sideOffset:l,alignOffset:u,collisionBoundary:d=`clipping-ancestors`,collisionPadding:f,arrowPadding:p,sticky:m,disableAnchorTracking:h=!1,collisionAvoidance:g=ls,...v}=e,y=bm(),b=Fm(),x=Ss(),S=y.useState(`floatingRootContext`),C=y.useState(`mounted`),w=y.useState(`open`),T=y.useState(`openChangeReason`),E=y.useState(`activeTriggerElement`),D=y.useState(`modal`),O=y.useState(`openMethod`),k=y.useState(`positionerElement`),A=y.useState(`instantType`),j=y.useState(`transitionStatus`),M=y.useState(`adaptiveOrigin`),N=_.useRef(null),P=Fa(k),F=Uu({anchor:a,floatingRootContext:S,positionMethod:o,mounted:C,side:s,sideOffset:l,align:c,alignOffset:u,arrowPadding:p,collisionBoundary:d,collisionPadding:f,sticky:m,disableAnchorTracking:h,keepMounted:b,nodeId:x,collisionAvoidance:g,adaptiveOrigin:M}),I=S.useState(`domReferenceElement`);q(()=>{let e=I,t=N.current;if(e&&(N.current=e),t&&e&&e!==t){y.set(`instantType`,void 0);let e=new AbortController;return P(()=>{y.set(`instantType`,`trigger-change`)},e.signal),()=>{e.abort()}}},[I,P,y]);let L=D===!0&&T!==`trigger-hover`;Qm(w&&L,O===`touch`,k,E);let R=y.useStateSetter(`positionerElement`),z=qu(e,{open:w,side:F.side,align:F.align,anchorHidden:F.anchorHidden,instant:A},{styles:F.positionerStyles,transitionStatus:j,props:v,refs:[t,R],hidden:!C,inert:!w});return(0,Z.jsxs)(Lm.Provider,{value:F,children:[C&&L&&(0,Z.jsx)(zm,{inert:Zu(!w),cutout:E}),(0,Z.jsx)(Cs,{id:x,children:z})]})}),eh=_.createContext(void 0);function th(e){let t=_.useContext(eh);if(t===void 0&&!e)throw Error(ze(69));return t}var nh=_.createContext(void 0);function rh(){let[e,t]=_.useState(0),n=K(()=>(t(e=>e+1),()=>{t(e=>Math.max(0,e-1))}));return{context:_.useMemo(()=>({register:n}),[n]),hasClosePart:e>0}}var ih=_.forwardRef(function(e,t){let{render:n,className:r,style:i,initialFocus:a,finalFocus:o,...s}=e,c=bm(),l=Rm(),u=th(!0)!=null,{context:d,hasClosePart:f}=rh(),p=c.useState(`open`),m=c.useState(`openMethod`),h=c.useState(`instantType`),g=c.useState(`transitionStatus`),_=c.useState(`popupProps`),v=c.useState(`titleElementId`),y=c.useState(`descriptionElementId`),b=c.useState(`modal`),x=c.useState(`mounted`),S=c.useState(`openChangeReason`),C=c.useState(`activeTriggerElement`),w=c.useState(`floatingRootContext`),T=w.useState(`floatingId`),E=c.useState(`disabled`),D=c.useState(`openOnHover`),O=c.useState(`closeDelay`);Ia({open:p,ref:c.context.popupRef,onComplete(){p&&c.context.onOpenChangeComplete?.(!0)}}),Bl(w,{enabled:D&&!E,closeDelay:O});let k=a===void 0?sl(c.context.popupRef):a,A=b!==!1&&f;c.useSyncedValue(`focusManagerModal`,A);let j=c.useStateSetter(`popupElement`),M=lt(`div`,e,{state:{open:p,side:l.side,align:l.align,instant:h,transitionStatus:g},ref:[t,c.context.popupRef,j],props:[_,{id:T,role:`dialog`,...ol,"aria-labelledby":v,"aria-describedby":y,onKeyDown(e){u&&Qf.has(e.key)&&e.stopPropagation()}},Ku(g),s],stateAttributesMapping:bu});return(0,Z.jsx)(Ns,{context:w,openInteractionType:m,modal:A,disabled:!x||S===`trigger-hover`,initialFocus:k,returnFocus:o,restoreFocus:`popup`,previousFocusableElement:H(C)?C:void 0,nextFocusableElement:c.context.triggerFocusTargetRef,beforeContentFocusGuardRef:c.context.beforeContentFocusGuardRef,children:(0,Z.jsx)(nh.Provider,{value:d,children:M})})}),ah=`floating-popup-surface z-50 flex w-72 origin-(--transform-origin) flex-col gap-4 rounded-lg border p-2.5 popup-text-xs-plus text-[color:var(--popover-foreground)] outline-hidden duration-100 data-[side=bottom]:slide-in-from-top-2 data-[side=inline-end]:slide-in-from-left-2 data-[side=inline-start]:slide-in-from-right-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 data-open:animate-in data-open:fade-in-0 data-open:zoom-in-95 data-closed:animate-out data-closed:fade-out-0 data-closed:zoom-out-95`,oh=`floating-popup-surface flex min-h-0 w-full flex-col overflow-hidden rounded-xl border border-[color:color-mix(in_oklab,var(--border)_12%,transparent)] bg-[color:color-mix(in_oklab,var(--foreground)_5%,transparent)] p-0 text-[color:var(--foreground)]`;function sh({className:e,variant:t=`default`,...n}){return(0,Z.jsx)(`div`,{"data-slot":`popover-content`,"data-variant":t,className:X(t===`embedded-card`?oh:ah,e),...n})}function ch({...e}){return(0,Z.jsx)(Em,{"data-slot":`popover`,...e})}function lh({...e}){return(0,Z.jsx)(Nm,{"data-slot":`popover-trigger`,...e})}function uh({className:e,align:t=`center`,alignOffset:n=0,anchor:r,portalContainer:i,side:a=`bottom`,sideOffset:o=4,...s}){let c=td(i),l=_.useRef(null);return(0,Z.jsx)(Im,{container:c,ref:l,children:(0,Z.jsx)(ed,{container:l,children:(0,Z.jsx)($m,{align:t,alignOffset:n,anchor:r,side:a,sideOffset:o,className:`isolate z-50`,children:(0,Z.jsx)(ih,{render:(0,Z.jsx)(sh,{}),className:X(e),...s})})})})}function dh(e){let t=_.useRef(!0);t.current&&(t.current=!1,e())}function fh(e){return e==null||e.hasAttribute(`disabled`)||e.getAttribute(`aria-disabled`)===`true`}var ph=_.createContext(null);function mh(){let e=_.useContext(ph);if(e===null)throw Error(ze(60));return e}var hh=(e,t)=>Object.is(e,t);function gh(e,t,n){return e==null||t==null?Object.is(e,t):n(e,t)}function _h(e,t,n){return!e||e.length===0?-1:e.findIndex(e=>e!==void 0&&gh(e,t,n))}function vh(e,t,n){return e.filter(e=>!gh(t,e,n))}function yh(e){if(e==null)return``;if(typeof e==`string`)return e;try{return JSON.stringify(e)}catch{return String(e)}}function bh(e){return e!=null&&e.length>0&&typeof e[0]==`object`&&e[0]!=null&&`items`in e[0]}function xh(e){if(!Array.isArray(e))return e!=null&&`null`in e;let t=e;if(bh(t)){for(let e of t)for(let t of e.items)if(t&&t.value==null&&t.label!=null)return!0;return!1}for(let e of t)if(e&&e.value==null&&e.label!=null)return!0;return!1}function Sh(e,t){if(t&&e!=null)return t(e)??``;if(e&&typeof e==`object`){if(`label`in e&&e.label!=null)return String(e.label);if(`value`in e)return String(e.value)}return yh(e)}function Ch(e,t){return t&&e!=null?t(e)??``:e&&typeof e==`object`&&`value`in e&&`label`in e?yh(e.value):yh(e)}function wh(e,t,n){function r(){return Sh(e,n)}if(n&&e!=null)return n(e);if(e&&typeof e==`object`&&`label`in e&&e.label!=null)return e.label;if(t&&!Array.isArray(t))return t[e]??r();if(Array.isArray(t)){let n=t,i=bh(n)?n.flatMap(e=>e.items):n;if(typeof e!=`object`||!e){let t=i.find(t=>t.value===e);return t&&t.label!=null?t.label:r()}if(`value`in e){let t=i.find(t=>t&&t.value===e.value);if(t&&t.label!=null)return t.label}}return r()}function Th(e,t,n){return e.reduce((e,r,i)=>(i>0&&e.push(`, `),e.push((0,Z.jsx)(_.Fragment,{children:wh(r,t,n)},i)),e),[])}var Eh={id:e=>e.id,labelId:e=>e.labelId,modal:e=>e.modal,items:e=>e.items,itemToStringLabel:e=>e.itemToStringLabel,isItemEqualToValue:e=>e.isItemEqualToValue,value:e=>e.value,hasSelectedValue:e=>{let{value:t,multiple:n,itemToStringValue:r}=e;return t==null?!1:n&&Array.isArray(t)?t.length>0:Ch(t,r)!==``},hasNullItemLabel:(e,t)=>t?xh(e.items):!1,open:e=>e.open,mounted:e=>e.mounted,forceMount:e=>e.forceMount,transitionStatus:e=>e.transitionStatus,openMethod:e=>e.openMethod,activeIndex:e=>e.activeIndex,selectedIndex:e=>e.selectedIndex,isActive:(e,t)=>e.activeIndex===t,isSelected:(e,t)=>{let n=e.isItemEqualToValue,r=e.value;return e.multiple?Array.isArray(r)&&r.some(e=>gh(t,e,n)):gh(t,r,n)},isSelectedByFocus:(e,t)=>e.selectedIndex===t,popupProps:e=>e.popupProps,triggerProps:e=>e.triggerProps,triggerElement:e=>e.triggerElement,positionerElement:e=>e.positionerElement,listElement:e=>e.listElement,popupSide:e=>e.popupSide,scrollUpArrowVisible:e=>e.scrollUpArrowVisible,scrollDownArrowVisible:e=>e.scrollDownArrowVisible,hasScrollArrows:e=>e.hasScrollArrows};function Dh(e,t){return Math.max(0,e-t)}function Oh(e,t){if(t<=0)return 0;let n=rf(e,0,t),r=n,i=t-n,a=r<=1,o=i<=1;return a&&o?r<=i?0:t:a?0:o?t:n}function kh(e){let{id:t,value:n,defaultValue:r=null,onValueChange:i,open:a,defaultOpen:o=!1,onOpenChange:s,name:c,form:l,autoComplete:u,disabled:d=!1,readOnly:f=!1,required:p=!1,modal:m=!0,actionsRef:h,inputRef:g,onOpenChangeComplete:v,items:y,multiple:b=!1,itemToStringLabel:x,itemToStringValue:S,isItemEqualToValue:C=hh,highlightItemOnHover:w=!0,children:T}=e,{clearErrors:E}=wr(),{setDirty:D,setTouched:O,setFocused:k,validityData:A,setFilled:j,name:M,disabled:N,validation:P,validationMode:F}=Sr(),I=Fr({id:t}),L=N||d,R=M??c,[z,B]=Ha({controlled:n,default:b?r??it:r,name:`Select`,state:`value`}),[V,H]=Ha({controlled:a,default:o,name:`Select`,state:`open`}),U=_.useRef([]),W=_.useRef([]),ee=_.useRef(null),te=_.useRef(null),G=_.useRef(0),ne=_.useRef(null),re=_.useRef([]),ie=_.useRef(!1),ae=_.useRef(null),oe=_.useRef(null),se=_.useRef({allowSelectedMouseUp:!1,allowUnselectedMouseUp:!1,dragY:0}),ce=_.useRef(!1),{mounted:le,setMounted:ue,transitionStatus:de}=Va(V),{openMethod:fe,triggerProps:pe}=Mm(V),me=_e(()=>new nl({id:I,labelId:void 0,modal:m,multiple:b,itemToStringLabel:x,itemToStringValue:S,isItemEqualToValue:C,value:z,open:V,mounted:le,transitionStatus:de,items:y,forceMount:!1,openMethod:null,activeIndex:null,selectedIndex:null,popupProps:{},triggerProps:{},triggerElement:null,positionerElement:null,listElement:null,popupSide:null,scrollUpArrowVisible:!1,scrollDownArrowVisible:!1,hasScrollArrows:!1})).current,he=Zc(me,Eh.activeIndex),ge=Zc(me,Eh.selectedIndex),ve=Zc(me,Eh.triggerElement),ye=Zc(me,Eh.positionerElement),be=Qu(fe),xe=fe??be,Se=_.useMemo(()=>b?``:Ch(z,S),[b,z,S]),Ce=_.useMemo(()=>b&&Array.isArray(z)?z.map(e=>Ch(e,S)):Ch(z,S),[b,z,S]);Ua(zo(ve),I,z,K(()=>Ce),!L,c);let Te=_.useRef(z),Ee=b?Array.isArray(z)&&z.length>0:z!=null&&Se!==``;q(()=>{j(Ee)},[Ee,j]),q(function(){let e=z,t=!1;if(b){let n=Array.isArray(z)?z:[];t=n.length===0,e=n[n.length-1]}let n=t?-1:_h(re.current,e,C),r=n===-1?null:n;r===null&&(oe.current=null),!V&&me.set(`selectedIndex`,r)},[b,V,z,C,me]);function De(e){let t=A.initialValue;return Array.isArray(e)&&Array.isArray(t)?!af(e,t,(e,t)=>gh(e,t,C)):e!==t}Kd(z,()=>{E(R),D(De(z)),P.change(z)});let Oe=K((e,t)=>{s?.(e,t),!t.isCanceled&&(H(e),!e&&(t.reason===`focus-out`||t.reason===`outside-press`)&&(O(!0),k(!1),F===`onBlur`&&P.commit(z)))}),ke=K(()=>{ue(!1),me.update({activeIndex:null,openMethod:null,scrollUpArrowVisible:!1,scrollDownArrowVisible:!1}),v?.(!1)});Ia({enabled:!h,open:V,ref:ee,onComplete(){V||ke()}}),_.useImperativeHandle(h,()=>({unmount:ke}),[ke]);let Ae=K((e,t)=>{i?.(e,t),!t.isCanceled&&B(e)}),je=K(e=>{let t=Dh(e.scrollHeight,e.clientHeight),n=Oh(e.scrollTop,t),r=n>0,i=n<t;me.set(`scrollUpArrowVisible`,r),me.set(`scrollDownArrowVisible`,i)}),Me=Al({open:V,onOpenChange:Oe,elements:{reference:ve,floating:ye}}),Ne=Ps(Me,{enabled:!f&&!L,event:`mousedown`}),Pe=Bs(Me),Fe=Xl(Me,{enabled:!f&&!L,listRef:U,activeIndex:he,selectedIndex:ge,disabledIndices:it,onNavigate(e){e===null&&!V||me.set(`activeIndex`,e)},focusItemOnHover:w}),Ie=Zl(Me,{enabled:!f&&!L&&(V||!b),listRef:W,activeIndex:he,selectedIndex:ge,disabledIndices:e=>fh(U.current[e]),onMatch(e){V?me.set(`activeIndex`,e):Ae(re.current[e],$(Wa))},onTyping(e){ie.current=e}}),Le=_.useMemo(()=>we(Ie.reference,Fe.reference,Pe.reference,Ne.reference,pe),[Ne.reference,Ie.reference,Fe.reference,Pe.reference,pe]),Re=_.useMemo(()=>we(ol,Ie.floating,Fe.floating,Pe.floating),[Ie.floating,Fe.floating,Pe.floating]),ze=Fe.item??at;dh(()=>{me.update({popupProps:Re,triggerProps:Le})}),me.useSyncedValues({id:I,modal:m,multiple:b,value:z,open:V,mounted:le,transitionStatus:de,popupProps:Re,triggerProps:Le,items:y,itemToStringLabel:x,itemToStringValue:S,isItemEqualToValue:C,openMethod:xe});let Be=_.useMemo(()=>({store:me,floatingContext:Me,required:p,disabled:L,readOnly:f,multiple:b,highlightItemOnHover:w,setValue:Ae,setOpen:Oe,listRef:U,popupRef:ee,scrollHandlerRef:te,handleScrollArrowVisibility:je,scrollArrowsMountedCountRef:G,itemProps:ze,valueRef:ne,valuesRef:re,labelsRef:W,typingRef:ie,selectionRef:se,firstItemTextRef:ae,selectedItemTextRef:oe,validation:P,onOpenChangeComplete:v,alignItemWithTriggerActiveRef:ce,initialValueRef:Te}),[me,Me,p,L,f,b,w,Ae,Oe,ze,P,v,je]),Ve=Je(g,P.inputRef),He=b?void 0:R,Ue=_.useMemo(()=>!b||!Array.isArray(z)||!R?null:z.map(e=>{let t=Ch(e,S);return(0,Z.jsx)(`input`,{type:`hidden`,form:l,name:R,value:t,disabled:L},t)}),[b,z,l,R,S,L]);return(0,Z.jsxs)(ph.Provider,{value:Be,children:[T,(0,Z.jsx)(`input`,{...P.getValidationProps(L,{onFocus(){me.state.triggerElement?.focus({focusVisible:!0})},onChange(e){if(e.nativeEvent.defaultPrevented||L||f)return;let t=e.currentTarget.value,n=$(Wa,e.nativeEvent);function r(){if(b)return;let e=t.toLowerCase(),r=re.current.findIndex(t=>Ch(t,S).toLowerCase()===e||Sh(t,x).toLowerCase()===e);r===-1&&(r=re.current.findIndex((t,n)=>{let r=W.current[n];return r!=null&&r.toLowerCase()===e}));let i=re.current[r];i!=null&&Ae(i,n)}me.set(`forceMount`,!0),queueMicrotask(r)}}),id:I&&He==null?`${I}-hidden-input`:void 0,form:l,name:He,autoComplete:u,value:Se,disabled:L,required:p&&!(b&&Ee),readOnly:f,ref:Ve,style:R?Uo:Ho,tabIndex:-1,"aria-hidden":!0,suppressHydrationWarning:!0}),Ue]})}var Ah=5;function jh(e,t){let n=Mh(t);return e.clientX>=n.left-Ah&&e.clientX<=n.right+Ah&&e.clientY>=n.top-Ah&&e.clientY<=n.bottom+Ah}function Mh(e){let t=e.getBoundingClientRect(),n=R(e);if(Yr)return t;let r=n.getComputedStyle(e,`::before`),i=n.getComputedStyle(e,`::after`);if(r.content===`none`&&i.content===`none`)return t;let a=parseFloat(r.width)||0,o=parseFloat(r.height)||0,s=parseFloat(i.width)||0,c=parseFloat(i.height)||0,l=Math.max(t.width,a,s),u=Math.max(t.height,o,c),d=l-t.width,f=u-t.height;return{left:t.left-d/2,right:t.right+d/2,top:t.top-f/2,bottom:t.bottom+f/2}}var Nh=400,Ph={...vu,...yr,popupSide:e=>e?{"data-popup-side":e}:null,value:()=>null},Fh=_.forwardRef(function(e,t){let{render:n,className:r,id:i,disabled:a=!1,nativeButton:o=!0,style:s,...c}=e,{setTouched:l,setFocused:u,validationMode:d,state:f,disabled:p}=Sr(),{labelId:m}=jr(),{store:h,setOpen:g,selectionRef:v,validation:y,readOnly:b,required:x,alignItemWithTriggerActiveRef:S,disabled:C}=mh(),w=p||C||a,T=Zc(h,Eh.open),E=Zc(h,Eh.mounted),D=Zc(h,Eh.value),O=Zc(h,Eh.triggerProps),k=Zc(h,Eh.positionerElement),A=Zc(h,Eh.listElement),j=Zc(h,Eh.popupSide),M=Zc(h,Eh.id),N=Zc(h,Eh.labelId),P=Zc(h,Eh.hasSelectedValue),F=E&&k?j:null,I=i??M,L=gf(m,N);Fr({id:I});let R=zo(k),z=_.useRef(null),{getButtonProps:B,buttonRef:V}=Ge({disabled:w,native:o}),H=h.useStateSetter(`triggerElement`),U=Oa(),W=Oa(),ee=Oa();_.useEffect(()=>{if(T)return ee.start(Nh,()=>{v.current.allowUnselectedMouseUp=!0,v.current.allowSelectedMouseUp=!0}),()=>{ee.clear()};v.current={allowSelectedMouseUp:!1,allowUnselectedMouseUp:!1,dragY:0},W.clear()},[T,v,W,ee]);let te=we(O,{id:I,role:`combobox`,"aria-expanded":T,"aria-haspopup":`listbox`,"aria-controls":T?A?.id??di(k)?.id:void 0,"aria-labelledby":L,"aria-readonly":b||void 0,"aria-required":x||void 0,tabIndex:w?-1:0,onFocus(e){u(!0),T&&S.current&&g(!1,$(Wa,e.nativeEvent)),U.start(0,()=>{h.set(`forceMount`,!0)})},onBlur(e){Q(k,e.relatedTarget)||(l(!0),u(!1),d===`onBlur`&&y.commit(D))},onMouseDown(e){if(T)return;let t=Ue(e.currentTarget);function n(e){if(!z.current)return;let t=e.target;Q(z.current,t)||Q(R.current,t)||jh(e,z.current)||g(!1,$(io,e))}W.start(0,()=>{t.addEventListener(`mouseup`,n,{once:!0})})}},c,B),G=y.getValidationProps(w,te);G.role=`combobox`;let ne={...f,open:T,disabled:w,value:D,readOnly:b,popupSide:F,placeholder:!P};return lt(`button`,e,{ref:[t,z,V,H],state:ne,stateAttributesMapping:Ph,props:G})}),Ih={value:()=>null},Lh=_.forwardRef(function(e,t){let{className:n,render:r,children:i,placeholder:a,style:o,...s}=e,{store:c,valueRef:l}=mh(),u=Zc(c,Eh.value),d=Zc(c,Eh.items),f=Zc(c,Eh.itemToStringLabel),p=Zc(c,Eh.hasSelectedValue),m=!p&&a!=null&&i==null,h=Zc(c,Eh.hasNullItemLabel,m),g={value:u,placeholder:!p},_=null;return _=typeof i==`function`?i(u):i??(m&&!h?a:Array.isArray(u)?Th(u,d,f):wh(u,d,f)),lt(`span`,e,{state:g,ref:[t,l],props:[{children:_},s],stateAttributesMapping:Ih})}),Rh=_.forwardRef(function(e,t){let{render:n,className:r,style:i,...a}=e,{store:o}=mh();return lt(`span`,e,{state:{open:Zc(o,Eh.open)},ref:t,props:[{"aria-hidden":!0,children:`▼`},a],stateAttributesMapping:_u})}),zh=_.forwardRef(function(e,t){let{store:n}=mh(),r=Zc(n,Eh.mounted),i=Zc(n,Eh.forceMount);return r||i?(0,Z.jsx)(hs,{ref:t,...e}):null}),Bh=_.createContext(void 0);function Vh(){let e=_.useContext(Bh);if(!e)throw Error(ze(59));return e}function Hh(e,t){e&&Object.assign(e.style,t)}var Uh={position:`relative`,maxHeight:`100%`,overflowX:`hidden`,overflowY:`auto`},Wh={position:`fixed`},Gh=_.forwardRef(function(e,t){let{anchor:n,className:r,render:i,positionMethod:a,side:o,align:s,sideOffset:c,alignOffset:l,collisionBoundary:u=`clipping-ancestors`,collisionPadding:d,arrowPadding:f,sticky:p,disableAnchorTracking:m,alignItemWithTrigger:h=!0,collisionAvoidance:g=cs,style:v,...y}=e,{store:b,listRef:x,labelsRef:S,alignItemWithTriggerActiveRef:C,selectedItemTextRef:w,valuesRef:T,initialValueRef:E,popupRef:D,setValue:O,floatingContext:k}=mh(),A=Zc(b,Eh.open),j=Zc(b,Eh.mounted),M=Zc(b,Eh.modal),N=Zc(b,Eh.value),P=Zc(b,Eh.openMethod),F=Zc(b,Eh.positionerElement),I=Zc(b,Eh.triggerElement),L=Zc(b,Eh.isItemEqualToValue),R=Zc(b,Eh.transitionStatus),z=_.useRef(null),B=_.useRef(null),[V,H]=_.useState(h),U=j&&V&&P!==`touch`;!j&&V!==h&&H(h),_.useImperativeHandle(C,()=>U),Qm((U||M)&&A,P===`touch`,F,I);let W=Uu({anchor:n,floatingRootContext:k,positionMethod:a,mounted:j,side:o,sideOffset:c,align:s,alignOffset:l,arrowPadding:f,collisionBoundary:u,collisionPadding:d,sticky:p,disableAnchorTracking:m??U,collisionAvoidance:g,keepMounted:!0}),ee=U?`none`:W.side,te=U?Wh:W.positionerStyles,G={open:A,side:ee,align:W.align,anchorHidden:W.anchorHidden};q(()=>{b.set(`popupSide`,W.side)},[b,W.side]);let ne=qu(e,G,{styles:te,transitionStatus:R,props:y,refs:[t,b.useStateSetter(`positionerElement`)],hidden:!j,inert:!A}),re=_.useRef(0),ie=K(e=>{if(T.current.length===0)return;let t=re.current;if(re.current=e.size,e.size===t)return;let n=$(Wa);if(t!==0&&!b.state.multiple&&N!==null&&_h(T.current,N,L)===-1){let e=E.current,t=e!=null&&_h(T.current,e,L)!==-1?e:null;O(t,n),t===null&&(b.set(`selectedIndex`,null),w.current=null)}if(t!==0&&b.state.multiple&&Array.isArray(N)){let e=N.filter(e=>_h(T.current,e,L)!==-1);e.length!==N.length&&(O(e,n),e.length===0&&(b.set(`selectedIndex`,null),w.current=null))}if(A&&U){b.update({scrollUpArrowVisible:!1,scrollDownArrowVisible:!1});let e={height:``};Hh(F,e),Hh(D.current,e)}}),ae=_.useMemo(()=>({...W,side:ee,alignItemWithTriggerActive:U,setControlledAlignItemWithTrigger:H,scrollUpArrowRef:z,scrollDownArrowRef:B}),[W,ee,U,H]);return(0,Z.jsx)(cf,{elementsRef:x,labelsRef:S,onMapChange:ie,children:(0,Z.jsxs)(Bh.Provider,{value:ae,children:[j&&M&&(0,Z.jsx)(zm,{inert:Zu(!A),cutout:I}),ne]})})}),Kh=`base-ui-disable-scrollbar`,qh={className:Kh,getElement(e){return(0,Z.jsx)(`style`,{nonce:e,href:Kh,precedence:`base-ui:low`,children:`.${Kh}{scrollbar-width:none}.${Kh}::-webkit-scrollbar{display:none}`})}},Jh={...yu,...Ba},Yh=_.forwardRef(function(e,t){let{render:n,className:r,style:i,finalFocus:a,...o}=e,{store:s,popupRef:c,onOpenChangeComplete:l,setOpen:u,valueRef:d,firstItemTextRef:f,selectedItemTextRef:p,multiple:m,handleScrollArrowVisibility:h,scrollHandlerRef:g,listRef:v,highlightItemOnHover:y,floatingContext:b}=mh(),{side:x,align:S,alignItemWithTriggerActive:C,isPositioned:w,setControlledAlignItemWithTrigger:T}=Vh(),E=th(!0)!=null,D=Pu(),{nonce:O,disableStyleElements:k}=cp(),A=Zc(s,Eh.id),j=Zc(s,Eh.open),M=Zc(s,Eh.openMethod),N=Zc(s,Eh.mounted),P=Zc(s,Eh.popupProps),F=Zc(s,Eh.transitionStatus),I=Zc(s,Eh.triggerElement),L=Zc(s,Eh.positionerElement),z=Zc(s,Eh.listElement),B=_.useRef(!1),V=_.useRef(!1),H=_.useRef({}),U=Ma(),W=K(e=>{if(!L||!c.current||!V.current)return;let t=L.style.top===`0px`,n=L.style.bottom===`0px`;if(B.current||!C||!t&&!n){h(e);return}let r=Qh(L),i=$h(L.getBoundingClientRect().height,`y`,r),a=Ue(L),o=R(L),s=o.getComputedStyle(L),l=parseFloat(s.marginTop),u=parseFloat(s.marginBottom),d=Xh(o.getComputedStyle(c.current)),f=Math.min(a.documentElement.clientHeight-l-u,d),p=e.scrollTop,m=Zh(e),g=null,_=e=>{L.style.height=`${e}px`},v=t?m-p:p,y=Math.min(i+v,f);if(v<=1){let n=rf(v,0,f-i);n>0&&_(i+n),e.scrollTop=t?m:0,f-(i+n)<=1&&(B.current=!0),h(e);return}f-y>1?g=t?1/0:0:n&&p<m&&(g=p-(v-(i+v-f)));let b=Math.ceil(y);if(b!==0&&_(b),g!=null){let t=rf(g,0,Zh(e));Math.abs(e.scrollTop-t)>1&&(e.scrollTop=t)}b>=f-1&&(B.current=!0),h(e)});_.useImperativeHandle(g,()=>W,[W]),Ia({open:j,ref:c,onComplete(){j&&l?.(!0)}});let ee={open:j,transitionStatus:F,side:x,align:S};q(()=>{!L||!c.current||Object.keys(H.current).length||(H.current={top:L.style.top||`0`,left:L.style.left||`0`,right:L.style.right,height:L.style.height,bottom:L.style.bottom,minHeight:L.style.minHeight,maxHeight:L.style.maxHeight,marginTop:L.style.marginTop,marginBottom:L.style.marginBottom})},[c,L]),q(()=>{j||C||(V.current=!1,B.current=!1,Hh(L,H.current))},[j,C,L,c]),q(()=>{let e=c.current;if(!j||!I||!L||!e||C&&!w||s.state.transitionStatus===`ending`)return;if(V.current=!0,e.style.removeProperty(`--transform-origin`),!C){U.request(()=>h(z||e));return}let t=ng(e);try{let t=p.current;t?.isConnected||(t=!Eh.hasSelectedValue(s.state)&&f.current?.isConnected?f.current:null);let n=d.current,r=R(L),i=r.getComputedStyle(L),a=r.getComputedStyle(e),o=Ue(I),c=Qh(I),l=eg(I.getBoundingClientRect(),c),u=eg(L.getBoundingClientRect(),c),m=l.height,g=z||e,_=g.scrollHeight,b=parseFloat(a.borderBottomWidth),x=parseFloat(i.marginTop)||10,S=parseFloat(i.marginBottom)||10,C=parseFloat(i.minHeight)||100,w=Xh(a),E=o.documentElement.clientHeight-x-S,O=o.documentElement.clientWidth,k=E-l.bottom+m,A,j=D===`rtl`?l.right-u.width:l.left,M=0;if(t&&n){let e=eg(n.getBoundingClientRect(),c);A=eg(t.getBoundingClientRect(),c),j=u.left+(D===`rtl`?e.right-A.right:e.left-A.left);let r=e.top-l.top+e.height/2;M=A.top-u.top+A.height/2-r}let N=k+M+S+b,P=Math.min(E,N),F=E-x-S,V=N-P,U=O-5;L.style.left=`${rf(j,5,U-u.width)}px`,L.style.height=`${P}px`,L.style.maxHeight=`none`,L.style.marginTop=`${x}px`,L.style.marginBottom=`${S}px`,e.style.height=`100%`;let W=Zh(g),ee=V>=W-1;ee&&(P=Math.min(E,u.height)-(V-W));let te=l.top<20||l.bottom>E-20||Math.ceil(P)+1<Math.min(_,C),G=(r.visualViewport?.scale??1)!==1&&qr;if(te||G){Hh(L,H.current),T(!1);return}let ne=Math.max(C,P);if(ee){let e=Math.max(0,E-N);L.style.top=u.height>=F?`0`:`${e}px`,L.style.height=`${P}px`,g.scrollTop=Zh(g)}else L.style.bottom=`0`,g.scrollTop=V;if(A){let t=u.top,n=u.height,r=A.top+A.height/2,i=rf(n>0?(r-t)/n*100:50,0,100);e.style.setProperty(`--transform-origin`,`50% ${i}%`)}(ne===E||P>=w)&&(B.current=!0),h(g),y&&s.state.selectedIndex===null&&s.state.activeIndex===null&&v.current[0]!=null&&s.set(`activeIndex`,0)}finally{t()}},[s,j,L,I,d,f,p,c,h,C,T,U,z,v,y,D,w]),_.useEffect(()=>{if(!C||!L||!j)return;let e=R(L);function t(e){u(!1,$(lo,e))}return Lo(e,`resize`,t)},[u,C,L,j]);let te={...z?{role:`presentation`,"aria-orientation":void 0}:{role:`listbox`,"aria-multiselectable":m||void 0,id:`${A}-list`},onKeyDown(e){E&&Qf.has(e.key)&&e.stopPropagation()},onScroll(e){z||W(e.currentTarget)},...C&&{style:z?{height:`100%`}:Uh},className:!z&&C?qh.className:void 0},G=lt(`div`,e,{ref:[t,c],state:ee,stateAttributesMapping:Jh,props:[P,te,Ku(F),o]});return(0,Z.jsxs)(_.Fragment,{children:[!k&&qh.getElement(O),(0,Z.jsx)(Ns,{context:b,modal:!1,disabled:!N,openInteractionType:M,returnFocus:a,restoreFocus:!0,children:G})]})});function Xh(e){let t=e.maxHeight;return t.endsWith(`px`)&&parseFloat(t)||1/0}function Zh(e){return Dh(e.scrollHeight,e.clientHeight)}function Qh(e){return Cc.getScale(e)}function $h(e,t,n){return e/n[t]}function eg(e,t){return Ki({x:$h(e.x,`x`,t),y:$h(e.y,`y`,t),width:$h(e.width,`x`,t),height:$h(e.height,`y`,t)})}var tg=[[`transform`,`none`],[`scale`,`1`],[`translate`,`0 0`]];function ng(e){let{style:t}=e,n={};for(let[e,r]of tg)n[e]=t.getPropertyValue(e),t.setProperty(e,r,`important`);return()=>{for(let[e]of tg){let r=n[e];r?t.setProperty(e,r):t.removeProperty(e)}}}var rg=_.forwardRef(function(e,t){let{render:n,className:r,style:i,...a}=e,{store:o,scrollHandlerRef:s,multiple:c}=mh(),{alignItemWithTriggerActive:l}=Vh(),u=Zc(o,Eh.hasScrollArrows),d=Zc(o,Eh.openMethod),f={id:`${Zc(o,Eh.id)}-list`,role:`listbox`,"aria-multiselectable":c||void 0,onScroll(e){s.current?.(e.currentTarget)},...l&&{style:Uh},className:u&&d!==`touch`?qh.className:void 0};return lt(`div`,e,{ref:[t,o.useStateSetter(`listElement`)],props:[f,a]})}),ig=_.createContext(void 0);function ag(){let e=_.useContext(ig);if(!e)throw Error(ze(57));return e}var og=_.memo(_.forwardRef(function(e,t){let{render:n,className:r,style:i,value:a=null,label:o,disabled:s=!1,nativeButton:c=!1,...l}=e,u=_.useRef(null),d=ap({guess:!0,label:o,textRef:u}),{store:f,itemProps:p,setOpen:m,setValue:h,selectionRef:g,typingRef:v,valuesRef:y,multiple:b,selectedItemTextRef:x,disabled:S,readOnly:C}=mh(),w=S||s,T=Zc(f,Eh.isActive,d.index),E=Zc(f,Eh.open),D=Zc(f,Eh.isSelected,a),O=Zc(f,Eh.isSelectedByFocus,d.index),k=Zc(f,Eh.isItemEqualToValue),A=d.index,j=_.useRef(null);q(()=>{let e=y.current;return e[A]=a,()=>{delete e[A]}},[A,a,y]),q(()=>{let e=f.state.value,t=e;b&&Array.isArray(e)&&(t=e.length>0?e[e.length-1]:void 0),t!==void 0&&gh(a,t,k)&&(f.set(`selectedIndex`,A),u.current&&(x.current=u.current))},[A,b,k,f,a,x]);let M=_.useRef(`mouse`),N=_.useRef(!1),{getButtonProps:P,buttonRef:F}=Ge({disabled:w,focusableWhenDisabled:!0,native:c,composite:!0}),I={disabled:w,selected:D,highlighted:T};function L(e){if(S||C)return;let t=f.state.value;if(b){let n=Array.isArray(t)?t:[],r=D?vh(n,a,k):[...n,a];h(r,$(Ya,e))}else h(a,$(Ya,e)),m(!1,$(Ya,e))}function R(){g.current.dragY=0}let z={role:`option`,"aria-selected":D,tabIndex:E&&T?0:-1,onKeyDown(e){f.set(`activeIndex`,A),e.key===` `&&v.current&&e.preventDefault()},onClick(e){let t=M.current!==`touch`,n=e.nativeEvent.pointerType,r=t&&gi(e.nativeEvent)&&(n!==void 0||T),i=t&&!r&&!N.current;N.current=!1,!(w||i)&&L(e.nativeEvent)},onPointerEnter(e){M.current=e.pointerType},onPointerMove(e){if(e.pointerType===`mouse`&&e.buttons===1){let t=g.current;t.dragY+=e.movementY,t.dragY**2>=64&&(t.allowUnselectedMouseUp=!0)}},onPointerDown(e){M.current=e.pointerType,N.current=!0,R()},onMouseUp(){if(R(),w||M.current===`touch`||N.current)return;let e=!g.current.allowSelectedMouseUp&&D,t=!g.current.allowUnselectedMouseUp&&!D;e||t||(N.current=!0,j.current?.click(),N.current=!1)}},B=lt(`div`,e,{ref:[F,t,d.ref,j],state:I,props:[p,z,l,P]}),V=_.useMemo(()=>({selected:D,index:A,textRef:u,selectedByFocus:O}),[D,A,u,O]);return(0,Z.jsx)(ig.Provider,{value:V,children:B})})),sg=_.forwardRef(function(e,t){let{selected:n}=ag();return e.keepMounted||n?(0,Z.jsx)(cg,{...e,ref:t}):null}),cg=_.memo(_.forwardRef((e,t)=>{let{render:n,className:r,style:i,keepMounted:a,...o}=e,{selected:s}=ag(),c=_.useRef(null),{transitionStatus:l,setMounted:u}=Va(s),d=lt(`span`,e,{ref:[t,c],state:{selected:s,transitionStatus:l},props:[{"aria-hidden":!0,children:`✔️`},o],stateAttributesMapping:Ba});return Ia({open:s,ref:c,onComplete(){s||u(!1)}}),d})),lg=_.memo(_.forwardRef(function(e,t){let{index:n,textRef:r,selectedByFocus:i}=ag(),{firstItemTextRef:a,selectedItemTextRef:o}=mh(),{render:s,className:c,style:l,...u}=e;return lt(`div`,e,{ref:[_.useCallback(e=>{e&&(n===0&&(a.current=e),i&&(o.current=e))},[a,o,n,i]),t,r],props:u})})),ug=_.forwardRef(function(e,t){let{render:n,className:r,style:i,direction:a,keepMounted:o,...s}=e,c=a===`up`,{store:l,popupRef:u,listRef:d,handleScrollArrowVisibility:f,scrollArrowsMountedCountRef:p}=mh(),{side:m,scrollDownArrowRef:h,scrollUpArrowRef:g}=Vh(),_=Zc(l,c?Eh.scrollUpArrowVisible:Eh.scrollDownArrowVisible),v=Zc(l,Eh.openMethod),y=_&&v!==`touch`,b=Oa(),x=c?g:h,{mounted:S,transitionStatus:C,setMounted:w}=Va(y);q(()=>(p.current+=1,l.set(`hasScrollArrows`,!0),()=>{p.current=Math.max(0,p.current-1),p.current===0&&l.set(`hasScrollArrows`,!1)}),[l,p]),Ia({open:y,ref:x,onComplete(){y||w(!1)}});let T=lt(`div`,e,{ref:[t,x],state:{direction:a,visible:y,side:m,transitionStatus:C},props:[{"aria-hidden":!0,children:c?`▲`:`▼`,style:{position:`absolute`},onMouseMove(e){if(e.movementX===0&&e.movementY===0||b.isStarted())return;l.set(`activeIndex`,null);function t(){let e=l.state.listElement??u.current;if(!e)return;l.set(`activeIndex`,null),f(e);let n=Dh(e.scrollHeight,e.clientHeight),r=Oh(e.scrollTop,n),i=r===(c?0:n),a=d.current;if(r!==e.scrollTop&&(e.scrollTop=r),i){b.clear();return}if(a.length>0){let t=x.current?.offsetHeight||0;e.scrollTop=dg(a,c,r,e.clientHeight,t,n)}b.start(40,t)}b.start(40,t)},onMouseLeave(){b.clear()}},s],stateAttributesMapping:Ba});return S||o?T:null});function dg(e,t,n,r,i,a){if(t){let t=0,r=n+i-1;for(let n=0;n<e.length;n+=1){let i=e[n];if(i&&i.offsetTop>=r){t=n;break}}let o=Math.max(0,t-1),s=e[o];return o<t&&s?Oh(s.offsetTop-i,a):0}let o=e.length-1,s=n+r-i+1;for(let t=0;t<e.length;t+=1){let n=e[t];if(n&&n.offsetTop+n.offsetHeight>s){o=Math.max(0,t-1);break}}let c=Math.min(e.length-1,o+1),l=e[c];return c>o&&l?Oh(l.offsetTop+l.offsetHeight-r+i,a):a}var fg=_.forwardRef(function(e,t){return(0,Z.jsx)(ug,{...e,ref:t,direction:`down`})}),pg=_.forwardRef(function(e,t){return(0,Z.jsx)(ug,{...e,ref:t,direction:`up`})}),mg=_.createContext(void 0),hg=_.forwardRef(function(e,t){let{render:n,className:r,style:i,...a}=e,[o,s]=_.useState(),c=_.useMemo(()=>({labelId:o,setLabelId:s}),[o,s]),l=lt(`div`,e,{ref:t,props:[{role:`group`,"aria-labelledby":o},a]});return(0,Z.jsx)(mg.Provider,{value:c,children:l})}),gg=kh,_g=xt(`flex w-fit cursor-pointer items-center justify-between gap-1.5 border whitespace-nowrap font-medium transition-colors outline-none select-none disabled:cursor-not-allowed disabled:opacity-50 aria-invalid:border-[color:var(--destructive)] *:data-[slot=select-value]:line-clamp-1 *:data-[slot=select-value]:flex *:data-[slot=select-value]:items-center *:data-[slot=select-value]:gap-1.5 dark:aria-invalid:border-[color:color-mix(in_oklab,var(--destructive)_50%,transparent)] [&_svg]:pointer-events-none [&_svg]:shrink-0`,{variants:{placeholderTone:{default:`data-placeholder:text-[color:var(--foreground)]`,muted:`data-placeholder:text-[color:var(--muted-foreground)]`},radius:{default:`rounded-lg`,full:`rounded-full`},variant:{default:`${om} [&:not(:focus):not([aria-expanded=true]):not([data-open]):not([data-popup-open]):not([data-state=open]):hover]:!border-[color:color-mix(in_oklab,var(--border)_20%,transparent)] focus-visible:border-[color:color-mix(in_oklab,var(--border)_30%,transparent)] aria-expanded:border-[color:color-mix(in_oklab,var(--border)_30%,transparent)] data-popup-open:border-[color:color-mix(in_oklab,var(--border)_30%,transparent)] data-open:border-[color:color-mix(in_oklab,var(--border)_30%,transparent)]`,ghost:`border-transparent bg-transparent bg-clip-border text-[color:var(--foreground)] focus-visible:border-[color:var(--ring)] focus-visible:ring-2 focus-visible:ring-[color:color-mix(in_oklab,var(--ring)_30%,transparent)] hover:bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] hover:text-[color:var(--foreground)] active:bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] active:text-[color:var(--foreground)] aria-expanded:bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] aria-expanded:text-[color:var(--foreground)] data-open:bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] data-open:text-[color:var(--foreground)] data-popup-open:bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] data-popup-open:text-[color:var(--foreground)] data-[state=open]:bg-[color:color-mix(in_oklab,var(--input)_10%,transparent)] data-[state=open]:text-[color:var(--foreground)] ${ar}`},size:{sm:`h-6 gap-1 px-1.5 pr-1 py-0 text-xs/relaxed *:data-[slot=select-value]:gap-1 [&_svg:not([class*='size-'])]:size-3`,default:`h-7 px-2 py-0.5 text-xs/relaxed [&_svg:not([class*='size-'])]:size-3.5`,lg:`h-8 px-2.5 py-1 text-sm/relaxed [&_svg:not([class*='size-'])]:size-4`,xl:`h-10 px-3 py-1.5 text-base/relaxed [&_svg:not([class*='size-'])]:size-4`}},defaultVariants:{placeholderTone:`muted`,radius:`default`,variant:`default`,size:`default`}});function vg({className:e,...t}){return(0,Z.jsx)(hg,{"data-slot":`select-group`,className:X(`scroll-my-1 p-1`,e),...t})}function yg({className:e,...t}){return(0,Z.jsx)(Lh,{"data-slot":`select-value`,className:X(`flex min-w-0 flex-1 text-left`,e),...t})}function bg({className:e,placeholderTone:t=`muted`,radius:n=`default`,size:r=`default`,variant:i=`default`,children:a,...o}){return(0,Z.jsxs)(Fh,{"data-placeholder-tone":t,"data-radius":n,"data-slot":`select-trigger`,"data-size":r,"data-variant":i,className:X(`group/select-trigger`,_g({placeholderTone:t,radius:n,size:r,variant:i}),e),...o,children:[a,(0,Z.jsx)(Rh,{render:(0,Z.jsx)(dd,{openClassName:`group-aria-expanded/select-trigger:rotate-180 group-data-popup-open/select-trigger:rotate-180 group-data-open/select-trigger:rotate-180`})})]})}var xg=`group-aria-expanded/select-trigger:rotate-180 group-data-popup-open/select-trigger:rotate-180 group-data-open/select-trigger:rotate-180`;_.forwardRef(function({children:e,className:t,open:n,placeholderTone:r=`muted`,radius:i=`default`,size:a=`default`,variant:o=`default`,...s},c){return(0,Z.jsxs)(`button`,{"data-open":n?``:void 0,"data-placeholder-tone":r,"data-radius":i,"data-slot":`select-trigger`,"data-size":a,"data-variant":o,className:X(`group/select-trigger`,_g({placeholderTone:r,radius:i,size:a,variant:o}),t),ref:c,...s,children:[e,(0,Z.jsx)(dd,{openClassName:xg})]})});function Sg({className:e,children:t,side:n=`bottom`,sideOffset:r=4,align:i=`center`,alignOffset:a=0,alignItemWithTrigger:o=!0,...s}){let c=td(),l=_.useRef(null);return(0,Z.jsx)(zh,{container:c,ref:l,children:(0,Z.jsx)(ed,{container:l,children:(0,Z.jsx)(Gh,{side:n,sideOffset:r,align:i,alignOffset:a,alignItemWithTrigger:o,className:`isolate z-50`,children:(0,Z.jsxs)(Yh,{"data-slot":`select-content`,"data-align-trigger":o,className:X(`floating-popup-surface relative isolate z-50 max-h-(--available-height) min-w-32 origin-(--transform-origin) overflow-x-hidden overflow-y-auto rounded-lg border text-[color:var(--popover-foreground)] duration-100 data-[align-trigger=true]:w-(--anchor-width) data-[align-trigger=true]:animate-none data-[align-trigger=false]:w-max data-[align-trigger=false]:min-w-(--anchor-width) data-[side=bottom]:slide-in-from-top-2 data-[side=inline-end]:slide-in-from-left-2 data-[side=inline-start]:slide-in-from-right-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 data-open:animate-in data-open:fade-in-0 data-open:zoom-in-95 data-closed:animate-out data-closed:fade-out-0 data-closed:zoom-out-95`,`floating-popup-surface relative isolate z-50 max-h-(--available-height) min-w-32 origin-(--transform-origin) overflow-x-hidden overflow-y-auto rounded-lg border popup-text-xs-plus text-[color:var(--popover-foreground)] duration-100 data-[align-trigger=true]:w-(--anchor-width) data-[align-trigger=true]:animate-none data-[align-trigger=false]:w-max data-[align-trigger=false]:min-w-(--anchor-width) data-[side=bottom]:slide-in-from-top-2 data-[side=inline-end]:slide-in-from-left-2 data-[side=inline-start]:slide-in-from-right-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 data-open:animate-in data-open:fade-in-0 data-open:zoom-in-95 data-closed:animate-out data-closed:zoom-out-95`,e),...s,children:[(0,Z.jsx)(Dg,{}),(0,Z.jsx)(rg,{children:t}),(0,Z.jsx)(Og,{})]})})})})}function Cg(e,t){if(typeof e==`string`&&e.length>0)return e;if(typeof t==`string`||typeof t==`number`)return String(t)}function wg(e,t){let[n,r]=_.useState(!1);return _.useEffect(()=>{let n=e.current;if(!n||!t){r(!1);return}let i=()=>{r(n.scrollWidth>n.clientWidth+1)};if(i(),typeof ResizeObserver>`u`)return;let a=new ResizeObserver(i);return a.observe(n),n.firstElementChild instanceof HTMLElement&&a.observe(n.firstElementChild),()=>{a.disconnect()}},[t,e]),n?t:void 0}function Tg({children:e,title:t}){let n=_.useRef(null),r=wg(n,t);return t?(0,Z.jsx)(Ad,{className:`no-scrollbar min-w-0`,containerClassName:`min-w-0 flex-1`,preset:`compact`,side:`right`,viewportRef:n,watch:[t],children:(0,Z.jsx)(`span`,{className:`block min-w-max whitespace-nowrap pr-2`,title:r,children:e})}):(0,Z.jsx)(`span`,{className:`min-w-0 overflow-hidden text-ellipsis whitespace-nowrap`,children:e})}function Eg({className:e,children:t,title:n,...r}){let i=Cg(n,t);return(0,Z.jsxs)(og,{"data-slot":`select-item`,className:X(`relative flex min-h-7 w-full cursor-pointer items-center gap-2 rounded-md py-1 pr-8 pl-2 popup-text-xs-plus leading-normal tracking-tight font-medium outline-hidden select-none hover:bg-[color:color-mix(in_oklab,var(--foreground)_5%,transparent)] focus:bg-[color:color-mix(in_oklab,var(--foreground)_5%,transparent)] focus:text-[color:var(--accent-foreground)] not-data-[variant=destructive]:focus:**:text-[color:var(--accent-foreground)] data-disabled:pointer-events-none data-disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-3.5 *:[span]:last:flex *:[span]:last:items-center *:[span]:last:gap-2`,e),...r,children:[(0,Z.jsx)(lg,{className:`flex min-w-0 flex-1 gap-2 overflow-hidden whitespace-nowrap`,"data-slot":`select-item-text`,children:(0,Z.jsx)(Tg,{title:i,children:t})}),(0,Z.jsx)(sg,{render:(0,Z.jsx)(`span`,{className:`pointer-events-none absolute right-2 flex items-center justify-center`}),children:(0,Z.jsx)(A,{className:`pointer-events-none`})})]})}function Dg({className:e,...t}){return(0,Z.jsx)(pg,{"data-slot":`select-scroll-up-button`,className:X(`floating-popup-fill top-0 z-10 flex w-full cursor-pointer items-center justify-center py-1 [&_svg:not([class*='size-'])]:size-3.5`,e),...t,children:(0,Z.jsx)(dd,{direction:`up`})})}function Og({className:e,...t}){return(0,Z.jsx)(fg,{"data-slot":`select-scroll-down-button`,className:X(`floating-popup-fill bottom-0 z-10 flex w-full cursor-pointer items-center justify-center py-1 [&_svg:not([class*='size-'])]:size-3.5`,e),...t,children:(0,Z.jsx)(dd,{})})}var kg=_.createContext(void 0);function Ag(){return _.useContext(kg)}function jg(e={}){let{highlightItemOnHover:t,highlightedIndex:n,onHighlightedIndexChange:r}=Ve(),{ref:i,index:a}=ap(e),o=n===a,s=_.useRef(null),c=Je(i,s);return{compositeProps:{tabIndex:o?0:-1,onFocus(){r(a)},onMouseMove(){let e=s.current;if(!t||!e)return;let n=e.hasAttribute(`disabled`)||e.ariaDisabled===`true`;!o&&!n&&e.focus()}},compositeRef:c,index:a}}function Mg(e){let{render:t,className:n,style:r,state:i=at,props:a=it,refs:o=it,metadata:s,stateAttributesMapping:c,tag:l=`div`,...u}=e,{compositeProps:d,compositeRef:f}=jg({metadata:s});return lt(l,e,{state:i,ref:[f,...o],props:[d,...a,u],stateAttributesMapping:c})}var Ng=_.forwardRef(function(e,t){let{className:n,defaultPressed:r=!1,disabled:i=!1,form:a,onPressedChange:o,pressed:s,render:c,type:l,value:u,nativeButton:d=!0,style:f,...p}=e,m=kr(u||void 0),h=Ag(),g=h?.value??[],v=h?void 0:r,y=(i||h?.disabled)??!1,[b,x]=Ha({controlled:h?m!==void 0&&g.indexOf(m)>-1:s,default:v,name:`Toggle`,state:`pressed`}),{getButtonProps:S,buttonRef:C}=Ge({disabled:y,native:d}),w={disabled:y,pressed:b},T=[C,t],E=[{"aria-pressed":b,onClick(e){let t=!b,n=$(Wa,e.nativeEvent);o?.(t,n),!n.isCanceled&&(m&&h?.setGroupValue?.(m,t,n),!n.isCanceled&&x(t))}},p,S],D=lt(`button`,e,{enabled:!h,state:w,ref:T,props:E}),O=_.useMemo(()=>({disabled:y,focusableWhenDisabled:!1}),[y]);return h?(0,Z.jsx)(Mg,{tag:`button`,render:c,className:n,style:f,metadata:O,state:w,refs:T,props:E}):D}),Pg=xt(`group/toggle inline-flex cursor-pointer items-center justify-center gap-1 rounded-md text-xs font-medium whitespace-nowrap transition-all outline-none hover:bg-[color:color-mix(in_oklab,var(--foreground)_10%,transparent)] hover:text-[color:var(--foreground)] focus-visible:border-[color:var(--ring)] focus-visible:ring-[3px] focus-visible:ring-[color:color-mix(in_oklab,var(--ring)_50%,transparent)] disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-[color:var(--destructive)] aria-invalid:ring-[color:color-mix(in_oklab,var(--destructive)_20%,transparent)] ${or} dark:aria-invalid:ring-[color:color-mix(in_oklab,var(--destructive)_40%,transparent)] [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-3.5`,{variants:{variant:{default:`bg-transparent text-[color:color-mix(in_oklab,var(--foreground)_72%,transparent)]`,outline:`border border-[color:color-mix(in_oklab,var(--border)_12%,transparent)] bg-[color:color-mix(in_oklab,var(--input)_5%,transparent)] text-[color:color-mix(in_oklab,var(--foreground)_72%,transparent)] hover:bg-[color:color-mix(in_oklab,var(--foreground)_10%,transparent)] hover:text-[color:var(--foreground)] ${or} aria-pressed:hover:bg-[color:color-mix(in_oklab,var(--link)_12%,transparent)] aria-pressed:hover:text-[color:var(--foreground)] data-[pressed]:hover:bg-[color:color-mix(in_oklab,var(--link)_12%,transparent)] data-[pressed]:hover:text-[color:var(--foreground)] data-[state=on]:hover:bg-[color:color-mix(in_oklab,var(--link)_12%,transparent)] data-[state=on]:hover:text-[color:var(--foreground)]`},size:{default:`h-7 min-w-7 px-2`,sm:`h-6 min-w-6 rounded-[min(var(--radius-md),8px)] px-1.5 text-[0.625rem] [&_svg:not([class*='size-'])]:size-3`,lg:`h-8 min-w-8 px-2`}},defaultVariants:{variant:`default`,size:`default`}}),Fg=`data-composite-item-active`,Ig=[];function Lg(e){let{loopFocus:t=!0,orientation:n=`both`,grid:r,onLoop:i,direction:a,highlightedIndex:o,onHighlightedIndexChange:s,rootRef:c,enableHomeAndEndKeys:l=!1,stopEventPropagation:u,disabledIndices:d,modifierKeys:f=Ig}=e,[p,m]=_.useState(0),h=r!=null,g=_.useRef(null),v=Je(g,c),y=_.useRef([]),b=_.useRef(!1),x=o??p,S=K((e,t=!1)=>{if((s??m)(e),t){let t=y.current[e];np(g.current,t,a,n)}}),C=K(e=>{if(e.size===0||b.current)return;b.current=!0;let t=Array.from(e.keys()),r=t.find(e=>e?.hasAttribute(`data-composite-item-active`))??null,i=r?e.get(r)?.index??-1:-1;if(i!==-1)S(i);else if(Zi(t,x,d)){let e=Xi(t,{disabledIndices:d});qi(t,e)||S(e)}np(g.current,r,a,n)});q(()=>{if(d==null||o!=null||!b.current)return;let e=y.current;if(Zi(e,x,d)){let t=Xi(e,{disabledIndices:d});qi(e,t)||S(t)}},[d,o,x,y,S]);let w=K((e,t,n)=>i?i(e,t,n,y):n),T=K(e=>{let o=e.key===`Home`||e.key===`End`;if(!Qf.has(e.key)||!l&&o||Rg(e,f)||!g.current)return;let s=a===`rtl`,c=s?qf:Jf,p=s?Jf:qf,m=n===`vertical`?Kf:c,_=n===`vertical`?Gf:p,v=ri(e.nativeEvent);if(v!=null&&tp(v)&&!fh(v)){let t=v.selectionStart,n=v.selectionEnd,r=v.value;if(t==null||e.shiftKey||t!==n||e.key!==_&&t<r.length||e.key!==m&&t>0)return}let b=x,C=Ji(y,d),T=Yi(y,d);r!=null&&(b=r({disabledIndices:d,elementsRef:y,event:e,highlightedIndex:x,loopFocus:t,maxIndex:T,minIndex:C,onLoop:w,orientation:n,rtl:s}));let E=n!==`vertical`&&e.key===c||n!==`horizontal`&&e.key===`ArrowDown`,D=n!==`vertical`&&e.key===p||n!==`horizontal`&&e.key===`ArrowUp`;l&&(e.key===`Home`?b=C:e.key===`End`&&(b=T)),b===x&&(E||D)&&(t&&b===T&&E?(b=C,i&&(b=i(e,x,b,y))):t&&b===C&&D?(b=T,i&&(b=i(e,x,b,y))):b=Xi(y.current,{startingIndex:b,decrement:D,disabledIndices:d})),b!==x&&!qi(y.current,b)&&(u&&e.stopPropagation(),(h||o||E||D)&&e.preventDefault(),S(b,!0),queueMicrotask(()=>{y.current[b]?.focus()}))});return{props:{ref:v,onFocus(e){let t=g.current,n=ri(e.nativeEvent);!t||n==null||!tp(n)||n.setSelectionRange(0,n.value.length)},onKeyDown:T},highlightedIndex:x,onHighlightedIndexChange:S,elementsRef:y,onMapChange:C,relayKeyboardEvent:T}}function Rg(e,t){for(let n of $f)if(!t.includes(n)&&e.getModifierState(n))return!0;return!1}function zg(e){let{render:t,className:n,style:r,refs:i=it,props:a=it,state:o=at,stateAttributesMapping:s,highlightedIndex:c,onHighlightedIndexChange:l,orientation:u,grid:d,loopFocus:f,onLoop:p,enableHomeAndEndKeys:m,onMapChange:h,stopEventPropagation:g=!0,rootRef:v,disabledIndices:y,modifierKeys:b,highlightItemOnHover:x=!1,tag:S=`div`,...C}=e,{props:w,highlightedIndex:T,onHighlightedIndexChange:E,elementsRef:D,onMapChange:O,relayKeyboardEvent:k}=Lg({grid:d,loopFocus:f,onLoop:p,orientation:u,highlightedIndex:c,onHighlightedIndexChange:l,rootRef:v,stopEventPropagation:g,enableHomeAndEndKeys:m,direction:Pu(),disabledIndices:y,modifierKeys:b}),A=lt(S,e,{state:o,ref:i,props:[w,...a,C],stateAttributesMapping:s}),j=_.useMemo(()=>({highlightedIndex:T,onHighlightedIndexChange:E,highlightItemOnHover:x,relayKeyboardEvent:k}),[T,E,x,k]);return(0,Z.jsx)(Be.Provider,{value:j,children:(0,Z.jsx)(cf,{elementsRef:D,onMapChange:e=>{h?.(e),O(e)},children:A})})}var Bg=_.createContext(void 0);function Vg(){return _.useContext(Bg)}var Hg=_.forwardRef(function(e,t){let{defaultValue:n,disabled:r=!1,loopFocus:i=!0,onValueChange:a,orientation:o=`horizontal`,multiple:s=!1,value:c,className:l,render:u,style:d,...f}=e,p=th(!0),m=Vg(),h=c!==void 0||n!==void 0,g=(p?.disabled??!1)||(m?.disabled??!1)||r,[v,y]=Ha({controlled:c,default:c===void 0?n??it:void 0,name:`ToggleGroup`,state:`value`}),b=K((e,t,n)=>{let r;s?(r=v.slice(),t?r.push(e):r.splice(v.indexOf(e),1)):r=t?[e]:[],a?.(r,n),!n.isCanceled&&y(r)}),x={disabled:g,multiple:s,orientation:o},S=_.useMemo(()=>({disabled:g,setGroupValue:b,value:v,isValueInitialized:h}),[g,b,v,h]),C={role:`group`},w=lt(`div`,e,{enabled:!!p,state:x,ref:t,props:[C,f]});return(0,Z.jsx)(kg.Provider,{value:S,children:p?w:(0,Z.jsx)(zg,{render:u,className:l,style:d,state:x,refs:[t],props:[C,f],loopFocus:i,enableHomeAndEndKeys:!0,orientation:o})})}),Ug=_.createContext({size:`default`,variant:`default`,spacing:0,orientation:`horizontal`});function Wg({orientation:e,spacing:t,variant:n}){return t!==0||n!==`outline`?``:e===`vertical`?`[&>[data-slot]]:relative [&>[data-slot]:has(+[data-slot])]:border-b-0 [&>[data-slot][aria-pressed=true]+[data-slot]]:border-t-[color:color-mix(in_oklab,var(--border)_10%,transparent)] [&>[data-slot][data-pressed]+[data-slot]]:border-t-[color:color-mix(in_oklab,var(--border)_10%,transparent)] [&>[data-slot][data-state=on]+[data-slot]]:border-t-[color:color-mix(in_oklab,var(--border)_10%,transparent)]`:`[&>[data-slot]]:relative [&>[data-slot]:has(+[data-slot])]:border-r-0 [&>[data-slot][aria-pressed=true]+[data-slot]]:border-l-[color:color-mix(in_oklab,var(--border)_10%,transparent)] [&>[data-slot][data-pressed]+[data-slot]]:border-l-[color:color-mix(in_oklab,var(--border)_10%,transparent)] [&>[data-slot][data-state=on]+[data-slot]]:border-l-[color:color-mix(in_oklab,var(--border)_10%,transparent)]`}function Gg({className:e,variant:t,size:n,spacing:r=0,orientation:i=`horizontal`,children:a,...o}){let s=Wg({orientation:i,spacing:r,variant:t});return(0,Z.jsx)(Hg,{"data-slot":`toggle-group`,"data-variant":t,"data-size":n,"data-spacing":r,"data-orientation":i,style:{"--gap":r},className:X(`group/toggle-group flex w-fit flex-row items-center gap-[--spacing(var(--gap))] rounded-md data-[size=sm]:rounded-[min(var(--radius-md),8px)] data-vertical:flex-col data-vertical:items-stretch`,s,e),...o,children:(0,Z.jsx)(Ug.Provider,{value:{variant:t,size:n,spacing:r,orientation:i},children:a})})}function Kg({className:e,children:t,variant:n=`default`,size:r=`default`,...i}){let a=_.useContext(Ug);return(0,Z.jsx)(Ng,{"data-slot":`toggle-group-item`,"data-variant":a.variant||n,"data-size":a.size||r,"data-spacing":a.spacing,className:X(`shrink-0 group-data-[spacing=0]/toggle-group:rounded-none group-data-[spacing=0]/toggle-group:px-2 focus:z-10 focus-visible:z-10 group-data-horizontal/toggle-group:data-[spacing=0]:first:rounded-l-md group-data-vertical/toggle-group:data-[spacing=0]:first:rounded-t-md group-data-horizontal/toggle-group:data-[spacing=0]:last:rounded-r-md group-data-vertical/toggle-group:data-[spacing=0]:last:rounded-b-md`,Pg({variant:a.variant||n,size:a.size||r}),e),...i,children:t})}function qg({ariaLabel:e,name:t,onValueChange:n,options:r,value:i,variant:a=`default`}){let[o,s]=_.useState(()=>i??r[0]?.value??``),c=i??o;_.useEffect(()=>{if(i!==void 0){s(i);return}r.some(e=>e.value===o)||s(r[0]?.value??``)},[o,r,i]);function l(e){s(e),n?.(e)}return(0,Z.jsxs)(cd,{className:`min-w-0 gap-2`,children:[(0,Z.jsx)(Ud,{children:t}),(0,Z.jsx)(Gg,{"aria-label":e??t,className:`w-full`,onValueChange:e=>{let[t]=e;t&&l(t)},size:`default`,value:c?[c]:[],variant:`outline`,children:r.map(e=>(0,Z.jsxs)(Kg,{"aria-label":e.label,className:a===`dots`?`min-w-0 flex-1 gap-[7px]`:`min-w-0 flex-1`,value:e.value,children:[a===`dots`?(0,Z.jsx)(`span`,{"aria-hidden":`true`,className:`size-2 shrink-0 rounded-full`,style:{backgroundColor:e.indicatorColor??`currentColor`}}):null,e.label]},e.value))})]})}function Jg(e,t,n){return Math.min(n,Math.max(t,e))}function Yg(e){return String(e).split(`.`)[1]?.length??0}function Xg(e,t){let n=Yg(t),r=Number(e.toFixed(n));return String(r)}var Zg=new Set([`%`,`°`,`px`,`em`,`rem`,`vw`,`vh`,`vmin`,`vmax`,`s`,`ms`]);function Qg(e){return e.replace(/[.*+?^${}()|[\]\\]/g,`\\$&`)}function $g(e){let t=e.trim();return t===``||Zg.has(t)||/^[^\p{Letter}\p{Number}]+$/u.test(t)?``:` `}function e_(e,t){let n=t?.trim();if(!n||typeof n_(e)!=`number`)return e;let r=$g(n),i=RegExp(`(-?\\d+(?:\\.\\d+)?)(?:\\s*${Qg(n)})?`,`g`);return e.replaceAll(i,(e,t)=>`${t}${r}${n}`)}function t_(e,t,n){return e_(Xg(e,t),n)}function n_(e){let t=e.match(/-?\d+(?:\.\d+)?/),n=t?Number.parseFloat(t[0]):NaN;return Number.isFinite(n)?n:void 0}function r_(e){let t=Array.isArray(e)?e[0]:e;return typeof t==`number`?t:void 0}var i_=0;function a_(e){return i_+=1,`${e}:${i_}`}function o_({baseValue:e,className:t,disabled:n=!1,editValueLabel:r,markerCount:i,max:a=100,min:o=0,name:s,onValueChange:c,showFill:l,step:u=1,unit:d,value:f,valueLabel:p,variant:m=`continuous`}){let[h,g]=_.useState(f),v=_.useRef(null);_.useEffect(()=>{g(f)},[f]);let y=p&&h===f?e_(p,d):t_(h,u,d);function b(){return v.current??=a_(`slider:${s}`),{history:`merge`,historyGroup:v.current}}function x(){v.current=null}function S(e,t){let n=Jg(e,o,a);g(n),c?.(n,t)}function C(e,t){let n=n_(t),r=Jg((typeof n==`number`?n:h)+e*u,o,a);return S(r,b()),t_(r,u,d)}return(0,Z.jsxs)(cd,{className:X(`min-w-0 gap-1!`,t),"data-disabled":n,children:[(0,Z.jsxs)(`div`,{className:`flex w-full min-w-0 items-center justify-between gap-3`,children:[(0,Z.jsx)(Ud,{children:s}),(0,Z.jsx)(`div`,{className:`inline-flex h-5 shrink-0 items-center gap-1.5`,children:(0,Z.jsx)(qp,{ariaLabel:`${s}数值`,disabled:n,editAriaLabel:r,maxValueLabel:em(y,{max:a,min:o}),onCommit:e=>{let t=n_(e);typeof t==`number`&&S(t),x()},onStep:C,valueLabel:y})})]}),(0,Z.jsx)(Wp,{getAriaLabel:()=>s,markerCount:i,max:a,min:o,disabled:n,onValueChange:e=>{let t=r_(e);typeof t==`number`&&S(t,b())},onValueCommitted:x,resetValue:typeof e==`number`?[e]:void 0,showFill:l,step:u,value:[h],variant:m})]})}var s_=e=>{e.stopPropagation()};function c_({children:e,className:t,disabled:n,label:r,onClick:i,onPointerDown:a,spinOnClick:o=!1,tooltipSide:s=`top`}){let c=_.useRef(null);function l(){let e=c.current,t=typeof window<`u`&&window.matchMedia(`(prefers-reduced-motion: reduce)`).matches;if(!(!o||!e||t)){for(let t of e.getAnimations())t.cancel();e.animate([{transform:`rotate(0deg)`},{transform:`rotate(-360deg)`}],{duration:420,easing:`cubic-bezier(0.16, 1, 0.3, 1)`})}}function u(e){l(),i?.(),typeof e.currentTarget.blur==`function`&&e.currentTarget.blur()}return(0,Z.jsxs)(rd,{children:[(0,Z.jsx)(id,{render:(0,Z.jsx)(gr,{"aria-label":r,className:X(`data-[icon-active=true]:text-[color:var(--foreground)]`,t),"data-icon-active":!1,disabled:n,onClick:u,onPointerDown:a,size:`icon`,type:`button`,variant:`ghost`}),children:(0,Z.jsx)(`span`,{ref:c,className:`inline-flex origin-center`,children:e})}),(0,Z.jsx)(ad,{side:s,children:r})]})}function l_({collapsed:e,collapseDirection:t=`up`,collapseLabel:n=`收起参数面板`,expandLabel:r=`展开参数面板`,onResetControls:i,onToggleCollapsed:a,resetLabel:o=`重置全部参数`,title:s}){let c=t===`left`?e?`right`:`left`:t===`right`?e?`left`:`right`:e?`down`:`up`;return(0,Z.jsx)(`div`,{className:`shrink-0`,"data-collapsed":String(e),"data-slot":`properties-panel-header-shell`,children:(0,Z.jsxs)(`div`,{className:X(`flex h-9 touch-none items-center gap-3 pr-1 pl-3 hover:cursor-grab active:cursor-grabbing`,e?`justify-center px-1`:`justify-between`),"data-panel-drag-handle":``,"data-slot":`properties-panel-header`,children:[(0,Z.jsx)(`p`,{className:X(`m-0 min-w-0 truncate text-xs-plus font-medium text-[color:var(--foreground)]`,e&&`sr-only`),children:s}),(0,Z.jsxs)(`div`,{className:`inline-flex shrink-0 items-center gap-1`,children:[e||!i?null:(0,Z.jsx)(c_,{label:o,onClick:i,onPointerDown:s_,spinOnClick:!0,children:(0,Z.jsx)(O,{})}),a?(0,Z.jsx)(c_,{label:e?r:n,onClick:a,onPointerDown:s_,children:(0,Z.jsx)(dd,{direction:c})}):null]})]})})}var u_=`border-t border-[color:color-mix(in_oklab,var(--border)_8%,transparent)]`,d_=44,f_=`flex min-h-0 flex-col overflow-x-hidden overflow-y-auto overscroll-contain`,p_=_.forwardRef(function({children:e,className:t,...n},r){return(0,Z.jsx)(`div`,{...n,ref:r,className:X(`floating-popup-surface toolcraft-panel-surface isolate border text-[color:var(--popover-foreground)] supports-backdrop-filter:backdrop-blur-2xl supports-backdrop-filter:backdrop-saturate-150`,t),children:e})}),m_=_.forwardRef(function({children:e,className:t,scrollFadeMode:n=`always`,stickyFooter:r,stickyFooterActive:i=!1,stickyFooterProgress:a=null,...o},s){let[c,l]=_.useState(null),[u,d]=_.useState(n===`always`),f=_.useCallback(e=>{if(l(e),typeof s==`function`){s(e);return}s&&(s.current=e)},[s]),p=_.Children.count(r)>0;if(_.useLayoutEffect(()=>{if(n!==`overflow`){d(!0);return}if(!c){d(!1);return}let e=()=>{d(c.scrollHeight>c.clientHeight+1)};e(),window.addEventListener(`resize`,e);let t=typeof ResizeObserver>`u`?null:new ResizeObserver(e);t?.observe(c);let r=c.firstElementChild;return r&&t?.observe(r),()=>{window.removeEventListener(`resize`,e),t?.disconnect()}},[n,c]),n===`overflow`&&!u){let n=(0,Z.jsx)(`div`,{...o,className:X(f_,p?`flex-1`:u_,t),ref:f,children:e});return p?(0,Z.jsx)(h_,{stickyFooter:r,stickyFooterActive:i,stickyFooterProgress:a,children:n}):n}let m=(0,Z.jsx)(Ad,{...o,className:X(`flex min-h-0 flex-col`,p&&`flex-1`,t),containerClassName:X(`flex min-h-0 flex-col`,p?`flex-1`:u_),height:d_,preset:`default`,showOppositeSide:!0,side:`bottom`,visibilityMode:`terminal`,viewportRef:f,children:e});return p?(0,Z.jsx)(h_,{stickyFooter:r,stickyFooterActive:i,stickyFooterProgress:a,children:m}):m});function h_({children:e,stickyFooter:t,stickyFooterActive:n,stickyFooterProgress:r}){let i=typeof r==`number`?{"--sticky-footer-progress":String(r)}:void 0;return(0,Z.jsxs)(`div`,{className:X(`flex min-h-0 flex-col`,u_),children:[e,(0,Z.jsx)(`div`,{className:`relative shrink-0 before:absolute before:inset-x-0 before:top-0 before:z-10 before:h-px before:origin-left before:scale-x-[var(--sticky-footer-progress,1)] before:bg-[color:var(--accent)] before:opacity-0 before:transition-[opacity,transform] before:duration-200 before:ease-out before:content-[''] data-[sticky-footer-active=true]:before:opacity-100`,"data-sticky-footer-progress":typeof r==`number`?r:void 0,"data-sticky-footer-active":n?`true`:void 0,"data-slot":`toolcraft-panel-sticky-actions`,style:i,children:t})]})}function g_({action:e,actionGroup:t,allowCompoundDividers:n,children:r,className:i,collapsed:a=!1,collapseLabel:o,collapsible:s=!1,expandLabel:c,flush:l=!1,onCollapsedChange:u,spacing:d=`default`,title:f,...p}){let m=t!==void 0,h=_.Children.toArray(r),g=f!=null&&f!==!1,v=!!(s&&a),y=n??h.length>1,b=(0,Z.jsx)(Fd,{className:X(!m&&(d===`technical`?`py-3`:`pt-2 pb-6`)),children:h.map((e,t)=>(0,Z.jsx)(zd,{allowCompoundDividers:y,compoundDividerPlacement:__({childCount:h.length,index:t,shouldRenderInnerDividers:y}),flush:l||m,children:e},b_(e,t)))});return(0,Z.jsxs)(Pd,{...p,className:X(!m&&`py-0`,g&&`gap-0`,m&&`p-3`,i),"data-collapsed":s?String(v):void 0,"data-toolcraft-section-action-group":t,"data-toolcraft-section-actions":m?``:void 0,children:[g?(0,Z.jsx)(Id,{action:e,collapsed:v,collapseLabel:o,collapsible:s,expandLabel:c,onCollapsedChange:u,children:(0,Z.jsx)(Bd,{children:f})}):null,s?(0,Z.jsx)(v_,{collapsed:v,children:b}):b]})}function __({childCount:e,index:t,shouldRenderInnerDividers:n}){return!n||e<=1?`both`:t===0?`bottom`:t===e-1?`top`:`both`}function v_({collapsed:e,children:t}){let[n,r]=_.useState(!e),[i,a]=_.useState(e),o=y_(`${e?`collapsed`:`expanded`}:${n?`mounted`:`unmounted`}`);_.useEffect(()=>{if(e){a(!0);return}if(n){a(!1);return}r(!0),a(!0);let t=window.requestAnimationFrame(()=>{a(!1)});return()=>window.cancelAnimationFrame(t)},[e,n]);function s(t){t.target!==t.currentTarget||!e||r(!1)}return n?(0,Z.jsx)(`div`,{"aria-hidden":e?`true`:void 0,className:X(`grid overflow-hidden transition-[grid-template-rows,opacity] duration-180 ease-out motion-reduce:transition-none`,i?`pointer-events-none grid-rows-[0fr] opacity-0`:`grid-rows-[1fr] opacity-100`),"data-collapsed":String(e),"data-slot":`panel-section-collapsible-body`,onTransitionEnd:s,children:(0,Z.jsx)(`div`,{className:`min-h-0 overflow-hidden`,"data-toolcraft-controls-mounting":o?`true`:void 0,children:t})}):null}function y_(e){let[t,n]=_.useState(()=>({dependency:e,isSuppressing:!0}));return _.useEffect(()=>{if(n({dependency:e,isSuppressing:!0}),typeof window>`u`)return;if(typeof window.requestAnimationFrame!=`function`){let t=window.setTimeout(()=>{n({dependency:e,isSuppressing:!1})},0);return()=>window.clearTimeout(t)}let t=0,r=window.requestAnimationFrame(()=>{t=window.requestAnimationFrame(()=>{n({dependency:e,isSuppressing:!1})})});return()=>{window.cancelAnimationFrame(r),window.cancelAnimationFrame(t)}},[e]),t.dependency!==e||t.isSuppressing}function b_(e,t){return _.isValidElement(e)&&e.key!==null?e.key:t}function x_({children:e,className:t,collapsed:n,collapseDirection:r=`up`,collapseLabel:i,collapsible:a=!0,contentTransitionSuppressionKey:o,defaultCollapsed:s=!1,expandLabel:c,onCollapsedChange:l,onResetControls:u,resetLabel:d,stickyFooterActive:f=!1,stickyFooterProgress:p=null,title:m}){let[h,g]=_.useState(s),v=a&&(n??h),{bodyChildren:y,stickyFooterChildren:b}=T_(C_(e)?e:(0,Z.jsx)(D_,{children:e})),x=S_(o===void 0?v:`${v}:${String(o)}`);function S(){let e=!v;g(e),l?.(e)}return(0,Z.jsxs)(p_,{className:X(`pointer-events-auto flex max-h-[calc(100dvh-1.25rem)] flex-col overflow-hidden rounded-lg p-0 w-[300px]`,t),"data-collapsed":String(v),"data-panel-id":`properties`,children:[(0,Z.jsx)(l_,{collapsed:v,collapseDirection:r,collapseLabel:i,expandLabel:c,onResetControls:u,onToggleCollapsed:a?S:void 0,resetLabel:d,title:m}),v?null:(0,Z.jsx)(m_,{"data-toolcraft-controls-mounting":x?`true`:void 0,"data-slot":`toolcraft-panel-content`,stickyFooter:b.length>0?b:void 0,stickyFooterActive:f,stickyFooterProgress:p,children:y})]})}function S_(e){let[t,n]=_.useState(()=>({dependency:e,isSuppressing:!0}));return _.useEffect(()=>{if(n({dependency:e,isSuppressing:!0}),typeof window>`u`)return;if(typeof window.requestAnimationFrame!=`function`){let t=window.setTimeout(()=>{n({dependency:e,isSuppressing:!1})},0);return()=>window.clearTimeout(t)}let t=0,r=window.requestAnimationFrame(()=>{t=window.requestAnimationFrame(()=>{n({dependency:e,isSuppressing:!1})})});return()=>{window.cancelAnimationFrame(r),window.cancelAnimationFrame(t)}},[e]),t.dependency!==e||t.isSuppressing}function C_(e){return _.Children.toArray(e).some(w_)}function w_(e){if(!_.isValidElement(e))return!1;if(e.type===_.Fragment){let t=e.props;return C_(t.children)}return e.type===Pd||e.type===g_||e.props[`data-toolcraft-panel-section`]!==void 0}function T_(e){let t=_.Children.toArray(e),n=t.length;for(;n>0&&E_(t[n-1]);)--n;return{bodyChildren:t.slice(0,n),stickyFooterChildren:t.slice(n)}}function E_(e){return _.isValidElement(e)?e.props[`data-toolcraft-section-actions`]!==void 0||e.props.actionGroup!==void 0:!1}function D_({children:e}){let t=_.Children.toArray(e),n=t.length>1;return(0,Z.jsx)(Pd,{className:`py-0`,children:(0,Z.jsx)(Fd,{className:`pt-2 pb-6`,children:t.map((e,t)=>(0,Z.jsx)(zd,{allowCompoundDividers:n,children:e},O_(e,t)))})})}function O_(e,t){return _.isValidElement(e)&&e.key!==null?e.key:t}var k_=_.createContext(void 0);function A_(e){let t=_.useContext(k_);if(!e&&t===void 0)throw Error(ze(27));return t}var j_=_.forwardRef(function(e,t){let{render:n,className:r,style:i,forceRender:a=!1,...o}=e,s=A_(),c=s.useState(`open`),l=s.useState(`nested`),u=s.useState(`mounted`);return lt(`div`,e,{state:{open:c,transitionStatus:s.useState(`transitionStatus`)},ref:[s.context.backdropRef,t],stateAttributesMapping:bu,props:[{role:`presentation`,hidden:!u,style:{userSelect:`none`,WebkitUserSelect:`none`}},o],enabled:a||!l})}),M_=_.forwardRef(function(e,t){let{render:n,className:r,style:i,disabled:a=!1,nativeButton:o=!0,...s}=e,c=A_(),l=c.useState(`open`),{getButtonProps:u,buttonRef:d}=Ge({disabled:a,native:o}),f={disabled:a};function p(e){l&&c.setOpen(!1,$(Xa,e.nativeEvent))}return lt(`button`,e,{state:f,ref:[t,d],props:[{onClick:p},s,u]})}),N_=_.createContext(void 0);function P_(){let e=_.useContext(N_);if(e===void 0)throw Error(ze(26));return e}var F_={...yu,...Ba,nestedDialogOpen(e){return e?{"data-nested-dialog-open":``}:null}},I_=_.forwardRef(function(e,t){let{render:n,className:r,style:i,finalFocus:a,initialFocus:o,...s}=e,c=A_(),l=c.useState(`descriptionElementId`),u=c.useState(`disablePointerDismissal`),d=c.useState(`floatingRootContext`),f=c.useState(`popupProps`),p=c.useState(`modal`),m=c.useState(`mounted`),h=c.useState(`nested`),g=c.useState(`nestedOpenDialogCount`),_=c.useState(`open`),v=c.useState(`openMethod`),y=c.useState(`titleElementId`),b=c.useState(`transitionStatus`),x=c.useState(`role`),S=d.useState(`floatingId`);P_(),Ia({open:_,ref:c.context.popupRef,onComplete(){_&&c.context.onOpenChangeComplete?.(!0)}});let C=o===void 0?sl(c.context.popupRef):o,w=g>0,T=c.useStateSetter(`popupElement`),E=lt(`div`,e,{state:{open:_,nested:h,transitionStatus:b,nestedDialogOpen:w},props:[f,{id:S,"aria-labelledby":y,"aria-describedby":l,role:x,...ol,hidden:!m,onKeyDown(e){Qf.has(e.key)&&e.stopPropagation()},style:{"--nested-dialogs":g}},s],ref:[t,c.context.popupRef,T],stateAttributesMapping:F_});return(0,Z.jsx)(Ns,{context:d,openInteractionType:v,disabled:!m,closeOnFocusOut:!u,initialFocus:C,returnFocus:a,modal:p!==!1,restoreFocus:`popup`,children:E})}),L_=_.forwardRef(function(e,t){let{keepMounted:n=!1,...r}=e,i=A_(),a=i.useState(`mounted`),o=i.useState(`modal`),s=i.useState(`open`);return a||n?(0,Z.jsx)(N_.Provider,{value:n,children:(0,Z.jsxs)(hs,{ref:t,...r,children:[a&&o===!0&&(0,Z.jsx)(zm,{ref:i.context.internalBackdropRef,inert:Zu(!s)}),e.children]})}):null});function R_({store:e,parentContext:t,isDrawer:n}){let r=e.useState(`open`),i=e.useState(`disablePointerDismissal`),a=e.useState(`modal`),o=e.useState(`popupElement`),s=e.useState(`floatingRootContext`),[c,l]=_.useState(0),[u,d]=_.useState(0),f=c===0,p=Bs(s,{outsidePressEvent(){return e.context.internalBackdropRef.current||e.context.backdropRef.current?`intentional`:{mouse:a===`trap-focus`?`sloppy`:`intentional`,touch:`sloppy`}},outsidePress(t){if(!e.context.outsidePressEnabledRef.current||`button`in t&&t.button!==0)return!1;if(`touches`in t){if(t.type===`touchend`){if(t.changedTouches.length!==1||t.touches.length!==0)return!1}else if(t.touches.length!==1)return!1}let n=ri(t);if(f&&!i){if(a){let t=e.context.internalBackdropRef.current,r=e.context.backdropRef.current;return t||r?t===n||r===n||Q(n,o)&&!n?.hasAttribute(`data-base-ui-portal`):!0}return!0}return!1},escapeKey:f});return Xm(r&&a===!0,o),e.useContextCallback(`onNestedDialogOpen`,(e,t)=>{l(e),d(t)}),q(()=>(t?.onNestedDialogOpen&&(r?t.onNestedDialogOpen(c+1,u+ +!!n):t.onNestedDialogOpen(0,0)),()=>{t?.onNestedDialogOpen&&r&&t.onNestedDialogOpen(0,0)}),[n,r,c,u,t]),_l(e,{activeTriggerProps:p.reference,inactiveTriggerProps:p.trigger,popupProps:p.floating,nestedOpenDialogCount:c,nestedOpenDrawerCount:u}),null}var z_={...Ol,modal:e=>e.modal,nested:e=>e.nested,nestedOpenDialogCount:e=>e.nestedOpenDialogCount,nestedOpenDrawerCount:e=>e.nestedOpenDrawerCount,disablePointerDismissal:e=>e.disablePointerDismissal,openMethod:e=>e.openMethod,descriptionElementId:e=>e.descriptionElementId,titleElementId:e=>e.titleElementId,viewportElement:e=>e.viewportElement,role:e=>e.role},B_=class extends nl{constructor(e,t,n){let r=new yl,i=V_(e,r,t,n);super(i,H_(r),z_)}setOpen=(e,t)=>{if(t.preventUnmountOnClose=()=>{this.set(`preventUnmountingOnClose`,!0)},!e&&t.trigger==null&&this.state.activeTriggerId!=null&&(t.trigger=this.state.activeTriggerElement??void 0),this.context.onOpenChange?.(e,t),t.isCanceled)return;this.state.floatingRootContext.dispatchOpenChange(e,t);let n={open:e};dl(n,e,t.trigger),this.update(n)}};function V_(e,t,n,r=!1){let i={...xl(),modal:!0,disablePointerDismissal:!1,viewportElement:null,descriptionElementId:void 0,titleElementId:void 0,openMethod:null,nested:!1,nestedOpenDialogCount:0,nestedOpenDrawerCount:0,role:`dialog`,...e};return i.floatingRootContext=Sl(t,n,r),i}function H_(e){return{popupRef:_.createRef(),backdropRef:_.createRef(),internalBackdropRef:_.createRef(),outsidePressEnabledRef:{current:!0},triggerElements:e,onOpenChange:void 0,onOpenChangeComplete:void 0}}function U_(e,t){let{children:n,open:r,defaultOpen:i=!1,onOpenChange:a,onOpenChangeComplete:o,disablePointerDismissal:s=!1,modal:c=!0,actionsRef:l,handle:u,triggerId:d,defaultTriggerId:f=null}=t,p=e===`drawer`,m=e===`alert-dialog`,h=m?!0:c,g=m||s,v=m?`alertdialog`:`dialog`,y=A_(!0),b={modal:h,disablePointerDismissal:g,nested:y!=null,role:v},x=cl((e,t)=>new B_({open:i,openProp:r,activeTriggerId:f,triggerIdProp:d,...b},e,t),!0);x.useControlledProp(`openProp`,r),x.useControlledProp(`triggerIdProp`,d),x.useSyncedValues(b),x.useContextCallback(`onOpenChange`,a),x.useContextCallback(`onOpenChangeComplete`,o);let S=x.useState(`open`),C=x.useState(`mounted`),w=x.useState(`payload`);vl(x,S),hl(x);let{forceUnmount:T}=gl(S,x);_.useImperativeHandle(l,()=>({unmount:T,close:()=>x.setOpen(!1,$(co))}),[T,x]);let E=S||C;return(0,Z.jsxs)(k_.Provider,{value:x,children:[u&&(0,Z.jsx)(ll,{handle:u,store:x}),E&&(0,Z.jsx)(R_,{store:x,parentContext:y?.context,isDrawer:p}),typeof n==`function`?n({payload:w}):n]})}function W_(e){return U_(`dialog`,e)}var G_=_.forwardRef(function(e,t){let{render:n,className:r,style:i,id:a,...o}=e,s=A_(),c=kr(a);return s.useSyncedValueWithCleanup(`titleElementId`,c),lt(`h2`,e,{ref:t,props:[{id:c},o]})});function K_({...e}){return(0,Z.jsx)(W_,{"data-slot":`sheet`,...e})}function q_({children:e,container:t,...n}){let r=td(t),i=_.useRef(null);return(0,Z.jsx)(L_,{"data-slot":`sheet-portal`,container:r,ref:i,...n,children:(0,Z.jsx)(ed,{container:i,children:e})})}function J_({className:e,...t}){return(0,Z.jsx)(j_,{"data-slot":`sheet-overlay`,className:X(`fixed inset-0 z-50 bg-black/80 transition-opacity duration-150 data-ending-style:opacity-0 data-starting-style:opacity-0 supports-backdrop-filter:backdrop-blur-xs`,e),...t})}function Y_({className:e,children:t,closeLabel:n=`关闭`,portalContainer:r,side:i=`right`,showCloseButton:a=!0,...o}){return(0,Z.jsxs)(q_,{container:r,children:[(0,Z.jsx)(J_,{}),(0,Z.jsxs)(I_,{"data-slot":`sheet-content`,"data-side":i,className:X(`fixed z-50 flex flex-col border-[color:color-mix(in_oklab,var(--border)_12%,transparent)] bg-[color:var(--background)] bg-clip-padding popup-text-xs-plus leading-relaxed shadow-lg transition duration-200 ease-in-out data-ending-style:opacity-0 data-starting-style:opacity-0 data-[side=bottom]:inset-x-0 data-[side=bottom]:bottom-0 data-[side=bottom]:h-auto data-[side=bottom]:border-t data-[side=bottom]:data-ending-style:translate-y-[2.5rem] data-[side=bottom]:data-starting-style:translate-y-[2.5rem] data-[side=left]:inset-y-0 data-[side=left]:left-0 data-[side=left]:h-full data-[side=left]:w-3/4 data-[side=left]:border-r data-[side=left]:data-ending-style:translate-x-[-2.5rem] data-[side=left]:data-starting-style:translate-x-[-2.5rem] data-[side=right]:inset-y-0 data-[side=right]:right-0 data-[side=right]:h-full data-[side=right]:w-3/4 data-[side=right]:border-l data-[side=right]:data-ending-style:translate-x-[2.5rem] data-[side=right]:data-starting-style:translate-x-[2.5rem] data-[side=top]:inset-x-0 data-[side=top]:top-0 data-[side=top]:h-auto data-[side=top]:border-b data-[side=top]:data-ending-style:translate-y-[-2.5rem] data-[side=top]:data-starting-style:translate-y-[-2.5rem] data-[side=left]:sm:max-w-sm data-[side=right]:sm:max-w-sm`,e),...o,children:[t,a&&(0,Z.jsxs)(M_,{"data-slot":`sheet-close`,render:(0,Z.jsx)(gr,{variant:`ghost`,className:`absolute top-4 right-4`,size:`icon-sm`}),children:[(0,Z.jsx)(F,{}),(0,Z.jsx)(`span`,{className:`sr-only`,children:n})]})]})]})}function X_({className:e,...t}){return(0,Z.jsx)(`div`,{"data-slot":`sheet-header`,className:X(`flex flex-col gap-1.5 p-6`,e),...t})}function Z_({className:e,...t}){return(0,Z.jsx)(G_,{"data-slot":`sheet-title`,className:X(`popup-text-xs-plus font-medium text-[color:var(--foreground)]`,e),...t})}var Q_=_.createContext(void 0);function $_(){let e=_.useContext(Q_);if(e===void 0)throw Error(ze(64));return e}var ev={tabActivationDirection:e=>({"data-activation-direction":e})},tv=_.forwardRef(function(e,t){let{className:n,defaultValue:r=0,onValueChange:i,orientation:a=`horizontal`,render:o,value:s,style:c,...l}=e,u=e.defaultValue!==void 0,d=_.useRef([]),[f,p]=_.useState(()=>new Map),[m,h]=Ha({controlled:s,default:r,name:`Tabs`,state:`value`}),g=s!==void 0,[v,y]=_.useState(()=>new Map),b=_.useRef(void 0),x=_.useCallback(e=>nv(v,e),[v]),[S,C]=_.useState(()=>({previousValue:m,tabActivationDirection:`none`})),{previousValue:w,tabActivationDirection:T}=S,E=T,D=!1;w!==m&&(E=rv(w,m,a,v),D=w!=null&&m!=null&&x(m)==null);let O=D?w:m,k=w!==O||T!==E;q(()=>{k&&C({previousValue:O,tabActivationDirection:E})},[O,k,E]);let A=K((e,t)=>{t.activationDirection=rv(m,e,a,v),i?.(e,t),!t.isCanceled&&h(e)}),j=K((e,t)=>{i?.(e,$(t,void 0,void 0,{activationDirection:`none`}))}),M=K((e,t)=>(p(n=>{let r=new Map(n);return r.set(e,t),r}),()=>{p(n=>{if(n.get(e)!==t)return n;let r=new Map(n);return r.delete(e),r})})),N=_.useCallback(e=>f.get(e),[f]),P=_.useCallback(e=>{for(let t of v.values())if(e===t.value)return t.id},[v]),F=_.useMemo(()=>({getTabElementBySelectedValue:x,getTabIdByPanelValue:P,getTabPanelIdByValue:N,onValueChange:A,orientation:a,registerMountedTabPanel:M,setTabMap:y,tabActivationDirection:E,value:m}),[x,P,N,A,a,M,y,E,m]),I=_.useMemo(()=>{for(let e of v.values())if(e.value===m)return e},[v,m]),L=_.useMemo(()=>{for(let e of v.values())if(!e.disabled)return e.value},[v]),R=_.useRef(!u),z=_.useRef(r),B=_.useRef(u),V=_.useRef(!1);q(()=>{if(g)return;function e(e,t){h(e),C({previousValue:e,tabActivationDirection:`none`}),j(e,t),R.current=!1}if(v.size===0){V.current&&m!==null&&!b.current?.isConnected&&e(null,oo);return}V.current=!0,b.current=v.keys().next().value;let t=I?.disabled,n=I==null&&m!==null;if(!t&&m===z.current&&(B.current=!1),B.current&&t&&m===z.current)return;let r=R.current;if(t||n){let n=L??null;if(m===n){R.current=!1;return}let i=oo;r?i=so:t&&(i=ao),e(n,i);return}r&&I!=null&&(j(m,so),R.current=!1)},[L,g,j,I,h,v,m]);let H=lt(`div`,e,{state:{orientation:a,tabActivationDirection:E},ref:t,props:l,stateAttributesMapping:ev});return(0,Z.jsx)(Q_.Provider,{value:F,children:(0,Z.jsx)(cf,{elementsRef:d,children:H})})});function nv(e,t){for(let[n,r]of e.entries())if(t===r.value)return n;return null}function rv(e,t,n,r){if(e==null||t==null)return`none`;let[i,a,o]=n===`horizontal`?[`left`,`left`,`right`]:[`top`,`up`,`down`],s=nv(r,e),c=nv(r,t);if(s==null||c==null)return s!==c&&(typeof e==`number`||typeof e==`string`)&&typeof e==typeof t?t>e?o:a:`none`;let l=s.getBoundingClientRect()[i],u=c.getBoundingClientRect()[i];return u<l?a:u>l?o:`none`}var iv=_.createContext(void 0);function av(){let e=_.useContext(iv);if(e===void 0)throw Error(ze(65));return e}var ov=_.forwardRef(function(e,t){let{className:n,disabled:r=!1,render:i,value:a,id:o,nativeButton:s=!0,style:c,...l}=e,{value:u,getTabPanelIdByValue:d,onValueChange:f,orientation:p,tabActivationDirection:m}=$_(),{activateOnFocus:h,registerTabResizeObserverElement:g,tabsListElement:v}=av(),{highlightedIndex:y,onHighlightedIndexChange:b}=Ve(),x=kr(o),{compositeProps:S,compositeRef:C,index:w}=jg({metadata:_.useMemo(()=>({disabled:r,id:x,value:a}),[r,x,a])}),T=a===u,E=_.useRef(!1),D=_.useRef(null),O=K(e=>{D.current?.(),D.current=e?g(e):null});q(()=>{if(E.current){E.current=!1;return}if(!(T&&w>-1&&y!==w))return;let e=v;if(e!=null){let t=ni(Ue(e));if(t&&Q(e,t))return}r||b(w)},[T,w,y,b,r,v]);let{getButtonProps:k,buttonRef:A}=Ge({disabled:r,native:s,focusableWhenDisabled:!0}),j=d(a),M=_.useRef(!1),N=_.useRef(!1);function P(e){f(a,$(Wa,e.nativeEvent,void 0,{activationDirection:`none`}))}function F(e){T||r||P(e)}function I(e){T||r||h&&(!M.current||N.current)&&P(e)}function L(e){if(T||r)return;M.current=!0,N.current=e.button===0;let t=Ue(e.currentTarget);function n(){M.current=!1,N.current=!1,t.removeEventListener(`pointerup`,n),t.removeEventListener(`pointercancel`,n)}t.addEventListener(`pointerup`,n),t.addEventListener(`pointercancel`,n)}return lt(`button`,e,{state:{disabled:r,active:T,orientation:p,tabActivationDirection:m},ref:[t,A,C,O],props:[S,{role:`tab`,"aria-controls":j,"aria-selected":T,id:x,onClick:F,onFocus:I,onPointerDown:L,[Fg]:T?``:void 0,onKeyDownCapture(){E.current=!0}},l,k],stateAttributesMapping:ev})}),sv={...ev,...Ba},cv=_.forwardRef(function(e,t){let{className:n,value:r,render:i,keepMounted:a=!1,style:o,...s}=e,{value:c,getTabIdByPanelValue:l,orientation:u,tabActivationDirection:d,registerMountedTabPanel:f}=$_(),p=kr(),{ref:m,index:h}=ap(),g=r===c,{mounted:v,transitionStatus:y,setMounted:b}=Va(g),x=!v,S=l(r),C={hidden:x,orientation:u,tabActivationDirection:d,transitionStatus:y},w=_.useRef(null),T=lt(`div`,e,{state:C,ref:[t,m,w],props:[{"aria-labelledby":S,hidden:x,id:p,role:`tabpanel`,tabIndex:g?0:-1,inert:Zu(!g),"data-index":h},s],stateAttributesMapping:sv});return Ia({open:g,ref:w,onComplete(){g||b(!1)}}),q(()=>{if(!(p==null||x&&!a))return f(r,p)},[x,a,r,p,f]),a||v?T:null}),lv=_.forwardRef(function(e,t){let{activateOnFocus:n=!1,className:r,loopFocus:i=!0,render:a,style:o,...s}=e,{orientation:c,setTabMap:l,tabActivationDirection:u}=$_(),[d,f]=_.useState(0),[p,m]=_.useState(null),h=_.useRef(new Set),g=_.useRef(new Set),v=_.useRef(null);q(()=>{if(typeof ResizeObserver>`u`)return;let e=new ResizeObserver(()=>{h.current.forEach(e=>{e()})});return v.current=e,p&&e.observe(p),g.current.forEach(t=>{e.observe(t)}),()=>{e.disconnect(),v.current=null}},[p]);let y=K(e=>(h.current.add(e),()=>{h.current.delete(e)})),b=K(e=>(g.current.add(e),v.current?.observe(e),()=>{g.current.delete(e),v.current?.unobserve(e)})),x={orientation:c,tabActivationDirection:u},S={"aria-orientation":c===`vertical`?`vertical`:void 0,role:`tablist`},C=_.useMemo(()=>({activateOnFocus:n,registerIndicatorUpdateListener:y,registerTabResizeObserverElement:b,tabsListElement:p}),[n,y,b,p]);return(0,Z.jsx)(iv.Provider,{value:C,children:(0,Z.jsx)(zg,{render:a,className:r,style:o,state:x,refs:[t,m],props:[S,s],stateAttributesMapping:ev,highlightedIndex:d,enableHomeAndEndKeys:!0,loopFocus:i,orientation:c,onHighlightedIndexChange:f,onMapChange:l,disabledIndices:it})})});function uv({className:e,orientation:t=`horizontal`,...n}){return(0,Z.jsx)(tv,{"data-slot":`tabs`,"data-orientation":t,className:X(`group/tabs flex gap-2 data-horizontal:flex-col`,e),...n})}var dv=xt(`group/tabs-list inline-flex w-fit items-center justify-center rounded-lg p-[3px] text-[color:var(--muted-foreground)] group-data-vertical/tabs:h-fit group-data-vertical/tabs:flex-col data-[variant=line]:rounded-none`,{variants:{size:{default:`group-data-horizontal/tabs:h-8`,header:`group-data-horizontal/tabs:h-10`,"header-lg":`group-data-horizontal/tabs:h-10`},variant:{control:`w-full rounded-md p-0 text-[color:color-mix(in_oklab,var(--foreground)_72%,transparent)] [&>[data-slot=tabs-trigger]]:relative [&>[data-slot=tabs-trigger]:has(+[data-slot=tabs-trigger])]:border-r-0 [&>[data-slot=tabs-trigger][data-active]+[data-slot=tabs-trigger]]:border-l-[color:color-mix(in_oklab,var(--border)_10%,transparent)]`,default:`bg-transparent`,line:`gap-1 bg-transparent pl-0`}},compoundVariants:[{className:`group-data-horizontal/tabs:h-7`,size:`default`,variant:`control`}],defaultVariants:{size:`default`,variant:`default`}});function fv({className:e,size:t=`default`,variant:n=`default`,...r}){return(0,Z.jsx)(lv,{"data-slot":`tabs-list`,"data-variant":n,"data-size":t,className:X(dv({size:t,variant:n}),e),...r})}function pv({className:e,...t}){return(0,Z.jsx)(ov,{"data-slot":`tabs-trigger`,className:X(`relative inline-flex h-[var(--tabs-trigger-height,calc(100%-1px))] flex-1 cursor-pointer items-center justify-center gap-1.5 rounded-md border border-transparent px-1.5 py-0.5 text-xs font-medium whitespace-nowrap text-[color:color-mix(in_oklab,var(--foreground)_60%,transparent)] transition-none group-data-vertical/tabs:w-full group-data-vertical/tabs:justify-start group-data-vertical/tabs:py-[calc(--spacing(1.25))] hover:text-[color:var(--foreground)] focus-visible:border-[color:var(--ring)] focus-visible:ring-[3px] focus-visible:ring-[color:color-mix(in_oklab,var(--ring)_50%,transparent)] focus-visible:outline-1 focus-visible:outline-ring disabled:pointer-events-none disabled:opacity-50 aria-disabled:pointer-events-none aria-disabled:opacity-50 dark:text-[color:var(--muted-foreground)] dark:hover:text-[color:var(--foreground)] [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-3.5`,`group-data-[size=header-lg]/tabs-list:px-2.5 group-data-[size=header-lg]/tabs-list:text-xs-plus`,`group-data-[variant=control]/tabs-list:h-full group-data-[variant=control]/tabs-list:min-w-0 group-data-[variant=control]/tabs-list:rounded-none group-data-[variant=control]/tabs-list:border-[color:color-mix(in_oklab,var(--border)_12%,transparent)] group-data-[variant=control]/tabs-list:bg-[color:color-mix(in_oklab,var(--input)_5%,transparent)] group-data-[variant=control]/tabs-list:px-2 group-data-[variant=control]/tabs-list:transition-all group-data-[variant=control]/tabs-list:first:rounded-l-md group-data-[variant=control]/tabs-list:last:rounded-r-md group-data-[variant=control]/tabs-list:hover:bg-[color:color-mix(in_oklab,var(--foreground)_10%,transparent)] group-data-[variant=control]/tabs-list:hover:text-[color:var(--foreground)] group-data-[variant=control]/tabs-list:data-active:border-[color:color-mix(in_oklab,var(--border)_10%,transparent)] group-data-[variant=control]/tabs-list:data-active:bg-[color:color-mix(in_oklab,var(--link)_12%,transparent)] group-data-[variant=control]/tabs-list:data-active:text-[color:var(--foreground)] group-data-[variant=control]/tabs-list:data-active:hover:bg-[color:color-mix(in_oklab,var(--link)_12%,transparent)] group-data-[variant=control]/tabs-list:data-active:hover:text-[color:var(--foreground)]`,`group-data-[variant=line]/tabs-list:bg-transparent group-data-[variant=line]/tabs-list:data-active:border-transparent group-data-[variant=line]/tabs-list:data-active:bg-transparent`,`${sr} dark:data-active:text-[color:var(--foreground)]`,`after:absolute after:bg-[color:var(--foreground)] after:opacity-0 after:transition-none group-data-horizontal/tabs:after:inset-x-0 group-data-horizontal/tabs:after:bottom-[var(--tabs-indicator-bottom,-5px)] group-data-horizontal/tabs:after:h-0.5 group-data-vertical/tabs:after:inset-y-0 group-data-vertical/tabs:after:-right-1 group-data-vertical/tabs:after:w-0.5 group-data-[variant=line]/tabs-list:data-active:after:opacity-100`,e),...t})}function mv({className:e,...t}){return(0,Z.jsx)(cv,{"data-slot":`tabs-content`,className:X(`flex-1 text-xs/relaxed outline-none`,e),...t})}var hv=``+new URL(`poster-0qKU1qpL.png`,import.meta.url).href,gv=``+new URL(`aurora--T_lSQe3.png`,import.meta.url).href,_v=``+new URL(`blueDrop-zJiSOMYV.png`,import.meta.url).href,vv=``+new URL(`chrome-CmWCbSDw.png`,import.meta.url).href,yv=``+new URL(`chromaticMetal-jaOj7GKS.png`,import.meta.url).href,bv=``+new URL(`frost-5TitiKWg.png`,import.meta.url).href,xv=``+new URL(`opal-Czi46gqK.png`,import.meta.url).href,Sv=``+new URL(`particleRibbon-BGLkfFRp.png`,import.meta.url).href,Cv=``+new URL(`plasma-75zRh8iH.png`,import.meta.url).href,wv=``+new URL(`refractiveBlob-B8wcL_wC.png`,import.meta.url).href,Tv=``+new URL(`siri-rPkpl1Xk.png`,import.meta.url).href,Ev=``+new URL(`spectrum-BQxb1ogg.png`,import.meta.url).href,Dv=``+new URL(`violetEmber-DHkKNL5C.png`,import.meta.url).href,Ov=``+new URL(`voiceWave-D1__H5Sf.png`,import.meta.url).href,kv=`// Generated from effect.wgsl for the native SwiftUI/Metal export.
// Do not edit this file independently of the WGSL source.
// language: metal2.1
#include <metal_stdlib>
#include <simd/simd.h>

using metal::uint;
struct DefaultConstructible {
    template<typename T>
    operator T() && {
        return T {};
    }
};

struct Uniforms {
    metal::float2 size;
    float time;
    float speed;
    float radius;
    float zoom;
    float warp;
    float ridgeAmt;
    float sharp;
    float shade;
    float sheen;
    float gloss;
    float shellMidAlpha;
    float shellEdgeAlpha;
    float exposure;
    float style;
    float edgeSoftness;
    float edgeGlow;
    float paletteCount;
    float glassEnabled;
    float glassOpacity;
    float contourDeform;
    float bandDensity;
    float chromaticShift;
    float metalScale;
    float metalStretch;
    float metalAngle;
    float metalOffset;
    float metalPhase;
    float metalEvolution;
    float metalRoughness;
    float metalDepth;
    float particleDensity;
    float ribbonCount;
    float ribbonWidth;
    float ribbonTwist;
    float ribbonFold;
    float ribbonBreath;
    float particleSize;
    float particleBloom;
    metal::float4 colorA;
    metal::float4 colorB;
    metal::float4 colorC;
    metal::float4 colorD;
    metal::float4 highlightColor;
    metal::float4 shellInner;
    metal::float4 shellMid;
    metal::float4 shellEdge;
    metal::float4 sheenColor;
    metal::float4 specColor;
    metal::float4 canvasColor;
    metal::float4 glowColor;
    metal::float4 paletteStop0_;
    metal::float4 paletteStop1_;
    metal::float4 paletteStop2_;
    metal::float4 paletteStop3_;
    metal::float4 paletteStop4_;
    metal::float4 paletteStop5_;
    metal::float4 paletteStop6_;
    metal::float4 paletteStop7_;
    metal::float4 paletteStop8_;
    metal::float4 paletteStop9_;
    metal::float4 paletteStop10_;
    metal::float4 paletteStop11_;
};
struct MfRamp {
    float n;
    char _pad1[12];
    metal::float3 s0_;
    metal::float3 s1_;
    metal::float3 s2_;
    metal::float3 s3_;
    metal::float3 s4_;
    metal::float3 s5_;
    metal::float3 s6_;
    metal::float3 s7_;
    metal::float3 s8_;
    metal::float3 s9_;
    metal::float3 s10_;
    metal::float3 s11_;
};
struct VOut {
    metal::float4 pos;
    metal::float2 uv;
    char _pad2[8];
};
struct type_7 {
    metal::float2 inner[3];
};
constant float GL_FU = 0.8817204;
constant float GL_BSIG_CLEAR = 0.018;
constant float GL_BSIG_GLASS = 0.0399;
constant float GL_KA = 6.0;
constant float GL_KG = 4.1209;
constant float GL_KWA = 0.5;
constant float GL_KR = 0.32;
constant float GL_GH = 1.7320508;
constant float GL_CLEAR_EA = 0.995;
constant float GL_CLEAR_EB = 1.04;

float mfEdgeD(
    float soft
) {
    return soft - 0.005;
}

metal::float3 mfEdgeGlow(
    metal::float3 col,
    metal::float2 uv,
    metal::float2 ctr,
    float rad,
    float soft_1,
    float glow,
    metal::float3 glowRGB
) {
    if (glow <= 0.0) {
        return col;
    }
    float r_3 = metal::length(uv - ctr);
    float outside = metal::smoothstep(rad - metal::max(soft_1, 0.0005), rad + metal::max(soft_1, 0.0005), r_3);
    return col + (glowRGB * ((glow * metal::exp(-(metal::max(r_3 - rad, 0.0)) * 11.0)) * outside));
}

metal::float3 mfRampPick(
    float idx,
    metal::float3 s0_,
    metal::float3 s1_,
    metal::float3 s2_,
    metal::float3 s3_,
    metal::float3 s4_,
    metal::float3 s5_,
    metal::float3 s6_,
    metal::float3 s7_,
    metal::float3 s8_,
    metal::float3 s9_,
    metal::float3 s10_,
    metal::float3 s11_
) {
    metal::float3 r = {};
    r = s0_;
    metal::float3 _e14 = r;
    r = (idx == 1.0) ? s1_ : _e14;
    metal::float3 _e18 = r;
    r = (idx == 2.0) ? s2_ : _e18;
    metal::float3 _e22 = r;
    r = (idx == 3.0) ? s3_ : _e22;
    metal::float3 _e26 = r;
    r = (idx == 4.0) ? s4_ : _e26;
    metal::float3 _e30 = r;
    r = (idx == 5.0) ? s5_ : _e30;
    metal::float3 _e34 = r;
    r = (idx == 6.0) ? s6_ : _e34;
    metal::float3 _e38 = r;
    r = (idx == 7.0) ? s7_ : _e38;
    metal::float3 _e42 = r;
    r = (idx == 8.0) ? s8_ : _e42;
    metal::float3 _e46 = r;
    r = (idx == 9.0) ? s9_ : _e46;
    metal::float3 _e50 = r;
    r = (idx == 10.0) ? s10_ : _e50;
    metal::float3 _e54 = r;
    r = (idx == 11.0) ? s11_ : _e54;
    metal::float3 _e58 = r;
    return _e58;
}

metal::float3 mfRampCyc(
    float tIn,
    float n,
    metal::float3 s0_1,
    metal::float3 s1_1,
    metal::float3 s2_1,
    metal::float3 s3_1,
    metal::float3 s4_1,
    metal::float3 s5_1,
    metal::float3 s6_1,
    metal::float3 s7_1,
    metal::float3 s8_1,
    metal::float3 s9_1,
    metal::float3 s10_1,
    metal::float3 s11_1
) {
    float k_3 = metal::clamp(metal::floor(n + 0.5), 1.0, 12.0);
    float x = metal::fract(tIn) * k_3;
    float i0_ = metal::min(metal::floor(x), k_3 - 1.0);
    float i1_ = ((i0_ + 1.0) >= k_3) ? 0.0 : i0_ + 1.0;
    metal::float3 _e33 = mfRampPick(i0_, s0_1, s1_1, s2_1, s3_1, s4_1, s5_1, s6_1, s7_1, s8_1, s9_1, s10_1, s11_1);
    metal::float3 _e34 = mfRampPick(i1_, s0_1, s1_1, s2_1, s3_1, s4_1, s5_1, s6_1, s7_1, s8_1, s9_1, s10_1, s11_1);
    return metal::mix(_e33, _e34, x - i0_);
}

metal::float3 mfRampLin(
    float tIn_1,
    float n_1,
    metal::float3 s0_2,
    metal::float3 s1_2,
    metal::float3 s2_2,
    metal::float3 s3_2,
    metal::float3 s4_2,
    metal::float3 s5_2,
    metal::float3 s6_2,
    metal::float3 s7_2,
    metal::float3 s8_2,
    metal::float3 s9_2,
    metal::float3 s10_2,
    metal::float3 s11_2
) {
    float k_4 = metal::clamp(metal::floor(n_1 + 0.5), 1.0, 12.0);
    float x_1 = metal::clamp(tIn_1, 0.0, 1.0) * (k_4 - 1.0);
    float i0_1 = metal::clamp(metal::floor(x_1), 0.0, metal::max(k_4 - 2.0, 0.0));
    metal::float3 _e33 = mfRampPick(i0_1, s0_2, s1_2, s2_2, s3_2, s4_2, s5_2, s6_2, s7_2, s8_2, s9_2, s10_2, s11_2);
    metal::float3 _e36 = mfRampPick(i0_1 + 1.0, s0_2, s1_2, s2_2, s3_2, s4_2, s5_2, s6_2, s7_2, s8_2, s9_2, s10_2, s11_2);
    return metal::mix(_e33, _e36, x_1 - i0_1);
}

MfRamp mfRampOf(
    float n_2,
    metal::float3 s0_3,
    metal::float3 s1_3,
    metal::float3 s2_3,
    metal::float3 s3_3,
    metal::float3 s4_3,
    metal::float3 s5_3,
    metal::float3 s6_3,
    metal::float3 s7_3,
    metal::float3 s8_3,
    metal::float3 s9_3,
    metal::float3 s10_3,
    metal::float3 s11_3
) {
    return MfRamp {n_2, {}, s0_3, s1_3, s2_3, s3_3, s4_3, s5_3, s6_3, s7_3, s8_3, s9_3, s10_3, s11_3};
}

metal::float3 mfRampCycR(
    float t,
    MfRamp r_1
) {
    metal::float3 _e15 = mfRampCyc(t, r_1.n, r_1.s0_, r_1.s1_, r_1.s2_, r_1.s3_, r_1.s4_, r_1.s5_, r_1.s6_, r_1.s7_, r_1.s8_, r_1.s9_, r_1.s10_, r_1.s11_);
    return _e15;
}

metal::float3 mfRampLinR(
    float t_1,
    MfRamp r_2
) {
    metal::float3 _e15 = mfRampLin(t_1, r_2.n, r_2.s0_, r_2.s1_, r_2.s2_, r_2.s3_, r_2.s4_, r_2.s5_, r_2.s6_, r_2.s7_, r_2.s8_, r_2.s9_, r_2.s10_, r_2.s11_);
    return _e15;
}

float lqHash(
    metal::float2 pIn
) {
    metal::float2 p_1 = {};
    p_1 = metal::fract(pIn * metal::float2(123.34, 456.21));
    metal::float2 _e7 = p_1;
    metal::float2 _e8 = p_1;
    metal::float2 _e9 = p_1;
    p_1 = _e7 + metal::float2(metal::dot(_e8, _e9 + metal::float2(45.32)));
    float _e17 = p_1.x;
    float _e19 = p_1.y;
    return metal::fract(_e17 * _e19);
}

float lqNoise(
    metal::float2 p_2
) {
    metal::float2 f = {};
    metal::float2 i_4 = metal::floor(p_2);
    f = metal::fract(p_2);
    metal::float2 _e4 = f;
    metal::float2 _e5 = f;
    metal::float2 _e7 = f;
    f = (_e4 * _e5) * (metal::float2(3.0) - (2.0 * _e7));
    float _e14 = lqHash(i_4);
    float _e19 = lqHash(i_4 + metal::float2(1.0, 0.0));
    float _e21 = f.x;
    float _e27 = lqHash(i_4 + metal::float2(0.0, 1.0));
    float _e32 = lqHash(i_4 + metal::float2(1.0, 1.0));
    float _e34 = f.x;
    float _e37 = f.y;
    return metal::mix(metal::mix(_e14, _e19, _e21), metal::mix(_e27, _e32, _e34), _e37);
}

metal::float2 lqFbm(
    metal::float2 pIn_1,
    float bs
) {
    metal::float2 p_3 = {};
    float s = 0.0;
    float a = 0.5;
    float m = 0.0;
    float vr = 0.0;
    float g = 1.0;
    int i_1 = 0;
    p_3 = pIn_1;
    float e = (-6.0 * bs) * bs;
    uint2 loop_bound = uint2(4294967295u);
    bool loop_init = true;
    while(true) {
        if (metal::all(loop_bound == uint2(0u))) { break; }
        loop_bound -= uint2(loop_bound.y == 0u, 1u);
        if (!loop_init) {
            int _e74 = i_1;
            i_1 = as_type<int>(as_type<uint>(_e74) + as_type<uint>(1));
        }
        loop_init = false;
        int _e18 = i_1;
        if (_e18 < 5) {
        } else {
            break;
        }
        {
            float _e21 = g;
            float b_1 = metal::exp(e * _e21);
            float _e24 = s;
            float _e25 = a;
            metal::float2 _e26 = p_3;
            float _e27 = lqNoise(_e26);
            s = _e24 + (_e25 * (0.5 + (b_1 * (_e27 - 0.5))));
            float _e35 = vr;
            float _e36 = a;
            float _e37 = a;
            vr = _e35 + ((_e36 * _e37) * (1.0 - (b_1 * b_1)));
            float _e44 = m;
            float _e45 = a;
            m = _e44 + _e45;
            float _e47 = a;
            a = _e47 * 0.5;
            float _e50 = g;
            g = _e50 * GL_KG;
            float _e54 = p_3.x;
            float _e58 = p_3.y;
            float _e63 = p_3.x;
            float _e67 = p_3.y;
            p_3 = metal::float2((0.8 * _e54) - (0.6 * _e58), (0.6 * _e63) + (0.8 * _e67)) * 2.03;
        }
    }
    float _e77 = s;
    float _e78 = m;
    float _e81 = vr;
    float _e84 = m;
    return metal::float2(_e77 / _e78, (GL_KR * metal::sqrt(_e81)) / _e84);
}

float lqRidge(
    float v,
    float k
) {
    return metal::pow(metal::clamp(1.0 - metal::abs((v * 2.0) - 1.0), 0.0, 1.0), k);
}

metal::float3 lqRamp(
    float v_1,
    metal::float3 cA,
    metal::float3 cB,
    metal::float3 cC,
    metal::float3 cD,
    constant Uniforms& u
) {
    metal::float3 c = {};
    c = metal::mix(cA, cB, metal::smoothstep(0.0, 0.45, v_1));
    metal::float3 _e10 = c;
    c = metal::mix(_e10, cC, metal::smoothstep(0.38, 0.72, v_1));
    metal::float3 _e15 = c;
    c = metal::mix(_e15, cD, metal::smoothstep(0.68, 1.0, v_1));
    metal::float3 _e20 = c;
    float _e23 = u.paletteCount;
    metal::float4 _e26 = u.paletteStop0_;
    metal::float4 _e30 = u.paletteStop1_;
    metal::float4 _e34 = u.paletteStop2_;
    metal::float4 _e38 = u.paletteStop3_;
    metal::float4 _e42 = u.paletteStop4_;
    metal::float4 _e46 = u.paletteStop5_;
    metal::float4 _e50 = u.paletteStop6_;
    metal::float4 _e54 = u.paletteStop7_;
    metal::float4 _e58 = u.paletteStop8_;
    metal::float4 _e62 = u.paletteStop9_;
    metal::float4 _e66 = u.paletteStop10_;
    metal::float4 _e70 = u.paletteStop11_;
    metal::float3 _e72 = mfRampLin(v_1, _e23, _e26.xyz, _e30.xyz, _e34.xyz, _e38.xyz, _e42.xyz, _e46.xyz, _e50.xyz, _e54.xyz, _e58.xyz, _e62.xyz, _e66.xyz, _e70.xyz);
    float _e75 = u.paletteCount;
    return (_e75 > 0.5) ? _e72 : _e20;
}

float lqRidgeS(
    metal::float2 vs,
    float k_1
) {
    float d_1 = GL_GH * vs.y;
    float _e7 = lqRidge(vs.x - d_1, k_1);
    float _e9 = lqRidge(vs.x, k_1);
    float _e15 = lqRidge(vs.x + d_1, k_1);
    return ((_e7 + (4.0 * _e9)) + _e15) / 6.0;
}

float lqStepS(
    metal::float2 vs_1,
    float a_1,
    float b
) {
    float d_2 = GL_GH * vs_1.y;
    return ((metal::smoothstep(a_1, b, vs_1.x - d_2) + (4.0 * metal::smoothstep(a_1, b, vs_1.x))) + metal::smoothstep(a_1, b, vs_1.x + d_2)) / 6.0;
}

float lqPowS(
    metal::float2 vs_2,
    float k_2
) {
    float d_3 = GL_GH * vs_2.y;
    return ((metal::pow(metal::clamp(vs_2.x - d_3, 0.0, 1.0), k_2) + (4.0 * metal::pow(metal::clamp(vs_2.x, 0.0, 1.0), k_2))) + metal::pow(metal::clamp(vs_2.x + d_3, 0.0, 1.0), k_2)) / 6.0;
}

metal::float3 glsFinishPresetFluid(
    metal::float3 colorIn,
    metal::float2 p_4,
    constant Uniforms& u
) {
    metal::float3 color = {};
    color = colorIn;
    metal::float3 _e3 = color;
    metal::float4 _e6 = u.highlightColor;
    float _e10 = u.shade;
    color = metal::mix(_e3, _e6.xyz, (_e10 * 0.22) * metal::smoothstep(0.15, 1.15, metal::dot(p_4, metal::float2(-0.32, 0.78))));
    metal::float3 _e22 = color;
    float _e25 = u.shade;
    color = _e22 * (1.0 - ((_e25 * 0.34) * metal::smoothstep(-0.1, 1.2, metal::dot(p_4, metal::float2(0.45, -0.62)))));
    metal::float3 _e39 = color;
    float _e42 = u.shade;
    color = _e39 * (1.0 - ((_e42 * 0.22) * metal::smoothstep(0.72, 1.08, metal::length(p_4))));
    metal::float3 _e53 = color;
    return metal::clamp(_e53, metal::float3(0.0), metal::float3(1.0));
}

metal::float3 glsFinishEmissionFluid(
    metal::float3 colorIn,
    metal::float2 p,
    constant Uniforms& u
) {
    metal::float3 color = colorIn;
    if (u.glassEnabled > 0.5) {
        color = metal::mix(
            color,
            u.highlightColor.xyz,
            u.shade * 0.22
                * metal::smoothstep(0.15, 1.15, metal::dot(p, metal::float2(-0.32, 0.78)))
        );
    }
    color *= 1.0 - u.shade * 0.34
        * metal::smoothstep(-0.1, 1.2, metal::dot(p, metal::float2(0.45, -0.62)));
    color *= 1.0 - u.shade * 0.22
        * metal::smoothstep(0.72, 1.08, metal::length(p));
    return metal::clamp(color, metal::float3(0.0), metal::float3(1.0));
}

metal::float2 glsSiriBand(
    metal::float2 q,
    float drift,
    float phaseOffset,
    float amplitude,
    float mainY,
    float envelope,
    float softness
) {
    float y = (amplitude * envelope) * metal::sin(((q.x * 1.0) + drift) + phaseOffset);
    float distanceToLine = metal::abs(q.y - y);
    float line = 0.018 / (metal::sqrt((distanceToLine * distanceToLine) + (softness * softness)) + 0.026);
    float bandDistance = metal::max(0.0, metal::max(q.y - metal::max(mainY, y), metal::min(mainY, y) - q.y));
    float band = 0.018 / (bandDistance + 0.075);
    return metal::float2(line, band);
}

metal::float3 glsSiriFluid(
    metal::float2 p_5,
    float t_2,
    constant Uniforms& u
) {
    metal::float3 color_1 = {};
    float _e4 = u.zoom;
    float scale_1 = 0.74 + (_e4 * 0.34);
    metal::float2 q_5 = p_5 / metal::float2(scale_1);
    float xNorm = q_5.x;
    float envelopeBase = metal::cos(1.5707964 * metal::min(metal::abs(0.9 * xNorm), 1.0));
    float envelope_1 = envelopeBase * envelopeBase;
    float low = 0.5 + (0.5 * metal::cos(t_2 * 0.37));
    float mid = 0.5 + (0.5 * metal::sin((t_2 * 0.51) + 1.2));
    float high = 0.5 + (0.5 * metal::cos((t_2 * 0.73) + 2.1));
    float drift_1 = t_2 * 2.4;
    float _e50 = u.ridgeAmt;
    float mainAmplitude = (0.25 + (_e50 * 0.075)) + (low * 0.018);
    float bandAmplitude = (mainAmplitude + (mid * 0.025)) + (high * 0.018);
    float mainY_1 = (mainAmplitude * envelope_1) * metal::sin((q_5.x * 1.1) + drift_1);
    float _e73 = u.warp;
    float separation = (1.85 + (_e73 * 0.2)) + (mid * 0.28);
    float _e83 = u.ridgeAmt;
    float softness_2 = (0.035 + ((1.0 - _e83) * 0.018)) + (mid * 0.006);
    metal::float2 _e94 = glsSiriBand(q_5, drift_1, -(separation), bandAmplitude, mainY_1, envelope_1, softness_2);
    metal::float2 _e98 = glsSiriBand(q_5, drift_1, -(separation) * 0.34, bandAmplitude, mainY_1, envelope_1, softness_2);
    metal::float2 _e101 = glsSiriBand(q_5, drift_1, separation * 0.34, bandAmplitude, mainY_1, envelope_1, softness_2);
    metal::float2 _e102 = glsSiriBand(q_5, drift_1, separation, bandAmplitude, mainY_1, envelope_1, softness_2);
    float w0_ = _e94.x + _e94.y;
    float w1_ = _e98.x + _e98.y;
    float w2_ = _e101.x + _e101.y;
    float w3_ = _e102.x + _e102.y;
    float total = ((w0_ + w1_) + w2_) + w3_;
    float dominant0_ = w0_ * w0_;
    float dominant1_ = w1_ * w1_;
    float dominant2_ = w2_ * w2_;
    float dominant3_ = w3_ * w3_;
    float dominantTotal = ((dominant0_ + dominant1_) + dominant2_) + dominant3_;
    metal::float4 _e127 = u.colorA;
    metal::float4 _e132 = u.colorC;
    metal::float4 _e138 = u.colorB;
    metal::float4 _e144 = u.colorD;
    metal::float3 spectral = ((((_e127.xyz * dominant0_) + (_e132.xyz * dominant1_)) + (_e138.xyz * dominant2_)) + (_e144.xyz * dominant3_)) / metal::float3(metal::max(dominantTotal, 0.0001));
    float energy = (1.0 - metal::exp(-(total) * 0.58)) * envelope_1;
    float mainDistance = metal::abs(q_5.y - mainY_1);
    float whiteCore = metal::exp((-(mainDistance) * mainDistance) / 0.0028) * envelope_1;
    metal::float4 _e170 = u.colorD;
    metal::float4 _e174 = u.colorB;
    float glassFill = u.glassEnabled > 0.5 ? 1.0 : 0.0;
    metal::float3 atmosphere = metal::mix(
        _e170.xyz, _e174.xyz, metal::smoothstep(-0.7, 0.7, q_5.y)) * 0.018 * glassFill;
    color_1 = atmosphere + ((spectral * energy) * 1.14);
    metal::float3 _e188 = color_1;
    metal::float4 _e191 = u.highlightColor;
    color_1 = _e188 + ((_e191.xyz * whiteCore) * (0.18 + (0.1 * low)));
    float emissionMask = metal::mix(
        metal::smoothstep(0.08, 0.25, energy + whiteCore * 0.12),
        1.0,
        glassFill
    );
    color_1 *= emissionMask;
    metal::float3 _e200 = color_1;
    metal::float3 _e203 = color_1;
    color_1 = _e200 / (metal::float3(1.0) + (_e203 * 0.18));
    metal::float3 _e208 = color_1;
    metal::float3 _e209 = glsFinishEmissionFluid(_e208, p_5, u);
    return _e209;
}

float glsSpectrumHeight(
    metal::float2 q_1,
    float t_3,
    float frequency,
    float phaseOffset_1,
    float amplitude_1
) {
    float x_2 = q_1.x * 2.15;
    float envelope_2 = metal::pow(4.0 / (4.0 + (x_2 * x_2)), 4.0);
    float breathing = 0.82 + (0.18 * metal::sin((t_3 * 0.48) + (phaseOffset_1 * 0.7)));
    float wave = metal::abs(metal::sin(((frequency * x_2) - (t_3 * 1.36)) + phaseOffset_1));
    return ((envelope_2 * amplitude_1) * breathing) * (0.28 + (0.72 * wave));
}

float glsSpectrumLayer(
    metal::float2 q_2,
    float height,
    float softness_1
) {
    return (1.0 - metal::smoothstep(metal::max(height - softness_1, 0.0), height + softness_1, metal::abs(q_2.y))) * metal::smoothstep(0.0, 0.045, height);
}

metal::float3 glsSpectrumFluid(
    metal::float2 p_6,
    float t_4,
    constant Uniforms& u
) {
    metal::float3 color_2 = {};
    float _e4 = u.zoom;
    float scale_2 = 0.74 + (_e4 * 0.34);
    metal::float2 q_6 = p_6 / metal::float2(scale_2);
    float _e13 = u.ridgeAmt;
    float amplitude_2 = 0.26 + (_e13 * 0.27);
    float _e20 = u.warp;
    float frequency_1 = 0.72 + (_e20 * 0.095);
    float _e27 = u.ridgeAmt;
    float softness_3 = 0.026 + ((1.0 - _e27) * 0.032);
    float _e39 = glsSpectrumHeight(q_6, t_4, frequency_1 * 0.82, -1.2, amplitude_2 * 0.72);
    float _e41 = glsSpectrumHeight(q_6, t_4, frequency_1, 0.45, amplitude_2);
    float _e47 = glsSpectrumHeight(q_6, t_4, frequency_1 * 1.17, 2.05, amplitude_2 * 0.82);
    float _e48 = glsSpectrumLayer(q_6, _e39, softness_3);
    float _e49 = glsSpectrumLayer(q_6, _e41, softness_3);
    float _e50 = glsSpectrumLayer(q_6, _e47, softness_3);
    float spectrumX = q_6.x * 2.15;
    float envelope_3 = metal::pow(4.0 / (4.0 + (spectrumX * spectrumX)), 4.0);
    float support = metal::exp((-(q_6.y) * q_6.y) / 0.00072) * envelope_3;
    float total_1 = (_e48 + _e49) + _e50;
    metal::float4 _e73 = u.colorB;
    metal::float4 _e78 = u.colorC;
    metal::float4 _e84 = u.colorD;
    metal::float3 spectral_1 = (((_e73.xyz * _e48) + (_e78.xyz * _e49)) + (_e84.xyz * _e50)) / metal::float3(metal::max(total_1, 0.001));
    metal::float4 _e94 = u.colorD;
    float glassFill = u.glassEnabled > 0.5 ? 1.0 : 0.0;
    color_2 = (_e94.xyz * 0.025 * glassFill)
            + (spectral_1 * (1.0 - metal::exp(-(total_1) * 0.86)));
    metal::float3 _e107 = color_2;
    metal::float4 _e110 = u.colorA;
    color_2 = _e107 + ((_e110.xyz * support) * 0.58);
    metal::float3 _e116 = color_2;
    metal::float3 _e119 = color_2;
    color_2 = _e116 / (metal::float3(1.0) + (_e119 * 0.2));
    metal::float3 _e124 = color_2;
    metal::float3 _e125 = glsFinishEmissionFluid(_e124, p_6, u);
    return _e125;
}

float glsAuroraLayer(
    metal::float2 p_7,
    float t_5,
    float offset,
    constant Uniforms& u
) {
    float drift_2 = (t_5 * 0.18) + (offset * 2.5);
    float _e11 = u.warp;
    float wave1_ = metal::sin(((p_7.x * (2.0 + (_e11 * 0.13))) + drift_2) + (offset * 6.0)) * 0.25;
    float wave2_ = metal::sin(((p_7.x * 3.7) + (drift_2 * 1.3)) + (offset * 4.0)) * 0.12;
    float wave3_ = metal::sin(((p_7.x * 7.2) + (drift_2 * 0.7)) + (offset * 8.0)) * 0.055;
    metal::float2 _e62 = lqFbm(metal::float2((p_7.x * 1.6) + (drift_2 * 0.35), (p_7.y * 0.8) + (offset * 3.0)), 0.018);
    float noiseValue = _e62.x;
    float center = ((((offset * 0.46) + wave1_) + wave2_) + wave3_) + ((noiseValue - 0.5) * 0.28);
    float dist = metal::abs(p_7.y - center);
    float _e81 = u.ridgeAmt;
    float glow_1 = metal::exp((-(dist) * dist) * (13.0 - (5.0 * _e81)));
    metal::float2 _e102 = lqFbm(metal::float2((p_7.x * 4.0) + (t_5 * 0.22), (p_7.y * 7.0) + (offset * 5.0)), 0.012);
    float shimmer = _e102.x;
    return glow_1 * (0.64 + (0.36 * shimmer));
}

metal::float3 glsAuroraFluid(
    metal::float2 p_8,
    float t_6,
    constant Uniforms& u
) {
    metal::float3 color_3 = {};
    float _e4 = u.zoom;
    metal::float2 q_7 = p_8 * (0.82 + (_e4 * 0.58));
    float _e11 = glsAuroraLayer(q_7, t_6, -0.72, u);
    float _e13 = glsAuroraLayer(q_7, t_6, 0.0, u);
    float _e15 = glsAuroraLayer(q_7, t_6, 0.72, u);
    metal::float4 _e18 = u.colorA;
    color_3 = _e18.xyz * (0.46 + (0.18 * (q_7.y + 1.0)));
    metal::float3 _e29 = color_3;
    metal::float4 _e32 = u.colorB;
    color_3 = _e29 + ((_e32.xyz * _e11) * 1.3);
    metal::float3 _e38 = color_3;
    metal::float4 _e41 = u.colorC;
    color_3 = _e38 + ((_e41.xyz * _e13) * 1.15);
    metal::float3 _e47 = color_3;
    metal::float4 _e50 = u.colorD;
    color_3 = _e47 + ((_e50.xyz * _e15) * 1.2);
    metal::float3 _e56 = color_3;
    metal::float4 _e59 = u.colorB;
    metal::float4 _e63 = u.colorD;
    color_3 = _e56 + ((metal::mix(_e59.xyz, _e63.xyz, 0.5) * metal::min(_e11 * _e15, _e13)) * 0.65);
    metal::float2 starUv = (q_7 + metal::float2(1.0)) * 18.0;
    metal::float2 starCell = metal::floor(starUv);
    float _e79 = lqHash(starCell);
    float starPoint = metal::exp(-(metal::dot(metal::fract(starUv) - metal::float2(0.5), metal::fract(starUv) - metal::float2(0.5))) * 90.0);
    float stars = (metal::step(0.965, _e79) * starPoint) * (0.55 + (0.45 * metal::sin((t_6 * (1.0 + (_e79 * 2.0))) + (_e79 * 6.28))));
    metal::float3 _e110 = color_3;
    metal::float4 _e113 = u.highlightColor;
    color_3 = _e110 + ((_e113.xyz * stars) * (1.0 - metal::clamp((_e11 + _e13) + _e15, 0.0, 1.0)));
    metal::float3 _e125 = color_3;
    metal::float3 _e128 = color_3;
    color_3 = _e125 / (metal::float3(1.0) + (_e128 * 0.28));
    metal::float3 _e133 = color_3;
    metal::float3 _e134 = glsFinishPresetFluid(_e133, p_8, u);
    return _e134;
}

metal::float2 glsRotate(
    metal::float2 p_9,
    float angle
) {
    float c_1 = metal::cos(angle);
    float s_1 = metal::sin(angle);
    return metal::float2((c_1 * p_9.x) - (s_1 * p_9.y), (s_1 * p_9.x) + (c_1 * p_9.y));
}

float glsNeuroShape(
    metal::float2 pIn_2,
    float t_7,
    constant Uniforms& u
) {
    metal::float2 p_10 = {};
    metal::float2 sineAccum = metal::float2(0.0);
    metal::float2 result = metal::float2(0.0);
    float scale = 8.0;
    int j = 0;
    float _e4 = u.zoom;
    p_10 = pIn_2 * (0.34 + (0.08 * _e4));
    uint2 loop_bound_1 = uint2(4294967295u);
    bool loop_init_1 = true;
    while(true) {
        if (metal::all(loop_bound_1 == uint2(0u))) { break; }
        loop_bound_1 -= uint2(loop_bound_1.y == 0u, 1u);
        if (!loop_init_1) {
            int _e60 = j;
            j = as_type<int>(as_type<uint>(_e60) + as_type<uint>(1));
        }
        loop_init_1 = false;
        int _e21 = j;
        if (_e21 < 11) {
        } else {
            break;
        }
        {
            metal::float2 _e24 = p_10;
            metal::float2 _e26 = glsRotate(_e24, 1.0);
            p_10 = _e26;
            metal::float2 _e27 = sineAccum;
            metal::float2 _e29 = glsRotate(_e27, 1.0);
            sineAccum = _e29;
            metal::float2 _e30 = p_10;
            float _e31 = scale;
            int _e33 = j;
            metal::float2 _e37 = sineAccum;
            metal::float2 layer = (((_e30 * _e31) + metal::float2(static_cast<float>(_e33))) + _e37) - metal::float2(t_7 * 0.34);
            metal::float2 _e43 = sineAccum;
            sineAccum = _e43 + metal::sin(layer);
            metal::float2 _e46 = result;
            float _e53 = scale;
            result = _e46 + ((metal::float2(0.5) + (0.5 * metal::cos(layer))) / metal::float2(_e53));
            float _e57 = scale;
            scale = _e57 * 1.16;
        }
    }
    float _e64 = result.x;
    float _e66 = result.y;
    return _e64 + _e66;
}

metal::float3 glsPlasmaFluid(
    metal::float2 p_11,
    float t_8,
    constant Uniforms& u
) {
    metal::float3 color_4 = {};
    float _e2 = glsNeuroShape(p_11, t_8, u);
    float _e5 = u.warp;
    float phase = (((_e2 * (10.0 + _e5)) + (p_11.x * 1.7)) - (p_11.y * 1.3)) - (t_8 * 0.52);
    float _e22 = u.ridgeAmt;
    float ridgeWidth = 0.62 - (0.24 * _e22);
    float _e32 = u.sharp;
    float primary = metal::pow(metal::abs(metal::cos(phase)), metal::max(1.3, _e32 * ridgeWidth));
    float _e52 = u.sharp;
    float secondary = metal::pow(metal::abs(metal::cos(((phase * 0.53) + (metal::atan2(p_11.y, p_11.x) * 2.0)) + (t_8 * 0.21))), metal::max(1.6, _e52 * (ridgeWidth + 0.1)));
    float filaments = metal::max(primary, secondary * 0.64);
    float core = metal::pow(primary, 4.0);
    float polarity = 0.5 + (0.5 * metal::sin((phase * 0.37) + (_e2 * 3.0)));
    metal::float4 _e75 = u.colorA;
    metal::float4 _e81 = u.colorD;
    color_4 = metal::mix(_e75.xyz * 0.42, _e81.xyz * 0.48, polarity * 0.46);
    metal::float3 _e89 = color_4;
    metal::float4 _e92 = u.colorB;
    color_4 = metal::mix(_e89, _e92.xyz, filaments * 0.72);
    metal::float3 _e97 = color_4;
    metal::float4 _e100 = u.colorC;
    color_4 = metal::mix(_e97, _e100.xyz, core * 0.68);
    metal::float3 _e105 = color_4;
    metal::float4 _e108 = u.highlightColor;
    color_4 = _e105 + ((_e108.xyz * metal::pow(core, 3.0)) * 0.16);
    metal::float3 _e116 = color_4;
    metal::float3 _e119 = color_4;
    color_4 = _e116 / (metal::float3(1.0) + (_e119 * 0.34));
    metal::float3 _e124 = color_4;
    metal::float3 _e125 = glsFinishPresetFluid(_e124, p_11, u);
    return _e125;
}

metal::float3 glsChromeFluid(
    metal::float2 p_12,
    float t_9,
    constant Uniforms& u
) {
    metal::float2 q_3 = {};
    int i_2 = 1;
    metal::float3 color_5 = {};
    float _e4 = u.zoom;
    q_3 = p_12 * (1.0 + (_e4 * 0.35));
    float _e13 = u.warp;
    float amplitude_3 = 0.028 * _e13;
    uint2 loop_bound_2 = uint2(4294967295u);
    bool loop_init_2 = true;
    while(true) {
        if (metal::all(loop_bound_2 == uint2(0u))) { break; }
        loop_bound_2 -= uint2(loop_bound_2.y == 0u, 1u);
        if (!loop_init_2) {
            int _e53 = i_2;
            i_2 = as_type<int>(as_type<uint>(_e53) + as_type<uint>(1));
        }
        loop_init_2 = false;
        int _e18 = i_2;
        if (_e18 <= 9) {
        } else {
            break;
        }
        {
            int _e21 = i_2;
            float fi = static_cast<float>(_e21);
            float _e25 = q_3.x;
            float _e30 = q_3.y;
            q_3.x = _e25 + ((amplitude_3 / fi) * metal::cos(((fi * 2.7) * _e30) + (t_9 * 0.46)));
            float _e40 = q_3.y;
            float _e45 = q_3.x;
            q_3.y = _e40 + ((amplitude_3 / fi) * metal::cos(((fi * 3.1) * _e45) - (t_9 * 0.4)));
        }
    }
    float _e59 = q_3.y;
    float _e62 = q_3.x;
    float denominator = metal::max(metal::abs(metal::sin(((t_9 * 0.24) - _e59) - _e62)), 0.045);
    float flare = metal::clamp(1.0 / denominator, 0.0, 18.0);
    float metal_ = metal::smoothstep(1.15, 7.5, flare);
    float _e77 = q_3.x;
    float _e79 = q_3.y;
    float _e83 = u.sharp;
    float fold = 0.5 + (0.5 * metal::cos(((_e77 - _e79) * (3.2 + (_e83 * 0.28))) + (t_9 * 0.32)));
    float value = metal::clamp((metal_ * 0.74) + (fold * 0.36), 0.0, 1.0);
    metal::float4 _e107 = u.colorD;
    metal::float4 _e111 = u.colorC;
    metal::float4 _e115 = u.colorB;
    metal::float4 _e119 = u.colorA;
    metal::float3 _e121 = lqRamp(value, _e107.xyz, _e111.xyz, _e115.xyz, _e119.xyz, u);
    color_5 = _e121;
    metal::float3 _e123 = color_5;
    metal::float4 _e126 = u.colorA;
    color_5 = metal::mix(_e123, _e126.xyz, metal::pow(metal_, 5.0) * 0.62);
    metal::float3 _e133 = color_5;
    metal::float3 _e134 = glsFinishPresetFluid(_e133, p_12, u);
    return _e134;
}

float glsChromaticMetalPhase(
    metal::float2 p,
    float t,
    constant Uniforms& u
) {
    float angle = u.metalAngle * 0.01745329252;
    float scale = metal::max(u.metalScale, 0.05);
    float stretch = metal::mix(0.48, 1.58, metal::clamp(u.metalStretch, 0.0, 1.0));
    metal::float2 q = glsRotate(p / scale, angle);
    q = metal::float2(q.x / stretch, q.y * stretch);
    float cycle = t * 0.46 + u.metalPhase * 6.28318530718;
    float evolution = metal::clamp(u.metalEvolution, 0.0, 2.0);
    q.x += metal::sin(q.y * 1.86 - cycle) * 0.095 * evolution;
    q.x += metal::sin((q.x + q.y) * 1.28 + cycle * 2.0 + 1.4) * 0.045 * evolution;
    q.y += metal::sin(q.x * 1.52 + cycle + 0.8) * 0.07 * evolution;
    float repeats = metal::max(u.bandDensity, 1.0);
    return q.x * repeats * 2.18
         + metal::sin(q.y * (1.3 + repeats * 0.26) - cycle) * 0.56 * evolution
         + metal::sin((q.x - q.y) * 1.34 + cycle * 2.0 + 1.7) * 0.27 * evolution
         + metal::sin((q.x * 0.72 + q.y) * 2.1 - cycle * 3.0 + 0.35) * 0.11 * evolution
         + metal::sin(cycle) * 0.1
         + metal::sin(cycle * 3.0 + 0.7) * 0.035
         + cycle
         + u.metalOffset * 6.28318530718;
}

float glsChromaticMetalTone(
    float phase,
    constant Uniforms& u
) {
    float wave = 0.5 + 0.5 * metal::cos(phase);
    float roughness = metal::clamp(u.metalRoughness, 0.0, 1.0);
    float depth = metal::clamp(u.metalDepth, 0.0, 1.0);
    float edge = 0.025 + roughness * 0.18;
    float broadReflection = metal::smoothstep(0.5 - edge, 0.5 + edge, wave);
    float hardReflection = metal::pow(wave, metal::mix(13.0, 4.0, roughness));
    float blackFold = metal::pow(1.0 - wave, metal::mix(9.0, 3.0, roughness));
    float body = metal::mix(wave, broadReflection, 0.2 + depth * 0.3);
    return metal::clamp(0.018 + body * (0.46 + depth * 0.12)
                        + hardReflection * (0.3 + depth * 0.42)
                        - blackFold * (0.07 + depth * 0.11), 0.0, 1.0);
}

metal::float3 glsChromaticMetalSample(
    metal::float2 p,
    float t,
    constant Uniforms& u
) {
    float phase = glsChromaticMetalPhase(p, t, u);
    float angle = u.metalAngle * 0.01745329252;
    metal::float2 brushP = glsRotate(p / metal::max(u.metalScale, 0.05), angle);
    float brushed = metal::sin(brushP.y * 146.0
                               + metal::sin(brushP.x * 11.0) * 0.58)
                  + 0.48 * metal::sin(brushP.y * 317.0 - brushP.x * 5.0);
    float brushAmount = 0.004 + metal::clamp(u.metalRoughness, 0.0, 1.0) * 0.014;
    float tone = metal::clamp(glsChromaticMetalTone(phase, u)
                              + brushed * brushAmount, 0.0, 1.0);
    return lqRamp(tone, u.colorD.xyz, u.colorB.xyz, u.colorC.xyz, u.colorA.xyz, u);
}

metal::float3 glsChromaticMetalFluid(
    metal::float2 p,
    float t,
    constant Uniforms& u
) {
    float angle = u.metalAngle * 0.01745329252;
    metal::float2 splitDirection = glsRotate(metal::float2(0.0, 1.0), angle);
    metal::float2 split = splitDirection * u.chromaticShift * 0.045;
    metal::float3 redSample = glsChromaticMetalSample(p + split, t, u);
    metal::float3 neutral = glsChromaticMetalSample(p, t, u);
    metal::float3 blueSample = glsChromaticMetalSample(p - split, t, u);
    metal::float3 optical = metal::float3(redSample.x, neutral.y, blueSample.z);
    float fringe = metal::clamp(metal::length(optical - neutral) * 4.0, 0.0, 1.0);
    metal::float3 color = metal::mix(neutral, optical,
        metal::clamp(u.chromaticShift * (0.72 + fringe * 0.28), 0.0, 1.0));
    float centerTone = glsChromaticMetalTone(glsChromaticMetalPhase(p, t, u), u);
    float glint = metal::pow(centerTone,
        metal::mix(12.0, 5.0, metal::clamp(u.metalRoughness, 0.0, 1.0)));
    color = metal::mix(color, u.highlightColor.xyz,
        glint * metal::clamp(u.metalDepth, 0.0, 1.0) * 0.06);
    float radial2 = metal::clamp(metal::dot(p, p), 0.0, 1.0);
    metal::float3 normal = metal::normalize(metal::float3(
        p, metal::sqrt(metal::max(1.0 - radial2, 0.0))));
    float roughness = metal::clamp(u.metalRoughness, 0.0, 1.0);
    float depth = metal::clamp(u.metalDepth, 0.0, 1.0);
    float key = metal::pow(metal::max(metal::dot(normal,
        metal::normalize(metal::float3(-0.48, 0.62, 0.62))), 0.0),
        metal::mix(7.0, 3.0, roughness));
    float fill = metal::pow(metal::max(metal::dot(normal,
        metal::normalize(metal::float3(0.7, -0.34, 0.63))), 0.0),
        metal::mix(10.0, 4.0, roughness));
    float limb = 1.0 - normal.z;
    float fresnel = metal::pow(limb, 3.0);
    float rim = metal::pow(limb, 10.0);
    color *= 0.86 + normal.z * 0.14;
    color = metal::mix(color, u.highlightColor.xyz, key * (0.05 + depth * 0.13));
    color = metal::mix(color, u.colorC.xyz, fill * (0.025 + depth * 0.07));
    color = metal::mix(color, u.colorD.xyz, fresnel * (0.12 + depth * 0.15));
    color = metal::mix(color, u.highlightColor.xyz, rim * (0.035 + depth * 0.055));
    return glsFinishPresetFluid(color, p, u);
}

metal::float3 glsOpalFluid(
    metal::float2 p_13,
    float t_10,
    constant Uniforms& u
) {
    float d = {};
    float a_2 = 0.0;
    int i_3 = 0;
    metal::float3 color_6 = {};
    float _e4 = u.zoom;
    metal::float2 q_8 = p_13 * (0.8 + (_e4 * 0.64));
    float _e12 = u.warp;
    float complexity = 0.76 + (_e12 * 0.085);
    d = -(t_10) * 0.42;
    uint2 loop_bound_3 = uint2(4294967295u);
    bool loop_init_3 = true;
    while(true) {
        if (metal::all(loop_bound_3 == uint2(0u))) { break; }
        loop_bound_3 -= uint2(loop_bound_3.y == 0u, 1u);
        if (!loop_init_3) {
            int _e48 = i_3;
            i_3 = as_type<int>(as_type<uint>(_e48) + as_type<uint>(1));
        }
        loop_init_3 = false;
        int _e25 = i_3;
        if (_e25 < 8) {
        } else {
            break;
        }
        {
            int _e28 = i_3;
            float fi_1 = static_cast<float>(_e28);
            float _e30 = a_2;
            float _e31 = d;
            float _e33 = a_2;
            a_2 = _e30 + metal::cos((fi_1 - _e31) - ((_e33 * q_8.x) * complexity));
            float _e40 = d;
            float _e44 = a_2;
            d = _e40 + metal::sin(((q_8.y * fi_1) * complexity) + _e44);
        }
    }
    float _e51 = d;
    d = _e51 + (t_10 * 0.42);
    float _e55 = d;
    float _e56 = a_2;
    metal::float2 c1_ = (metal::cos(q_8 * metal::float2(_e55, _e56)) * 0.6) + metal::float2(0.4);
    float _e65 = a_2;
    float _e66 = d;
    float c2_ = (metal::cos(_e65 + _e66) * 0.5) + 0.5;
    float _e76 = d;
    float _e77 = a_2;
    metal::float3 interference = metal::float3(0.5) + (0.5 * metal::cos(((metal::float3(c1_.x, c1_.y, c2_) * metal::cos(metal::float3(_e76, _e77, 2.5))) * 0.5) + metal::float3(0.5)));
    float tone = metal::fract(((((interference.x * 0.37) + (interference.y * 0.51)) + (interference.z * 0.73)) + (c1_.x * 0.22)) - (c1_.y * 0.15));
    metal::float4 _e115 = u.colorB;
    metal::float4 _e119 = u.colorC;
    metal::float4 _e123 = u.colorD;
    metal::float4 _e127 = u.colorA;
    metal::float3 _e129 = lqRamp(tone, _e115.xyz, _e119.xyz, _e123.xyz, _e127.xyz, u);
    color_6 = _e129;
    metal::float3 _e131 = color_6;
    metal::float4 _e134 = u.colorA;
    color_6 = metal::mix(_e131, _e134.xyz, 0.16 + (0.1 * interference.z));
    metal::float3 _e142 = color_6;
    metal::float3 _e145 = color_6;
    color_6 = _e142 / (metal::float3(1.0) + (_e145 * 0.16));
    metal::float3 _e150 = color_6;
    metal::float3 _e151 = glsFinishPresetFluid(_e150, p_13, u);
    return _e151;
}

metal::float3 glsFrostFluid(
    metal::float2 p_14,
    float t_11,
    constant Uniforms& u
) {
    metal::float2 q_4 = {};
    metal::float3 color_7 = {};
    float _e4 = u.zoom;
    q_4 = p_14 * (0.66 + (_e4 * 0.92));
    float _e13 = q_4.y;
    q_4.y = _e13 + (t_11 * 0.055);
    float _e19 = u.zoom;
    float blur = 0.011 + (0.006 * _e19);
    metal::float2 _e24 = q_4;
    metal::float2 _e32 = lqFbm((_e24 * 1.14) + metal::float2(t_11 * 0.055, 0.0), blur);
    metal::float2 _e34 = q_4;
    metal::float2 _e43 = lqFbm((_e34 * 1.14) + metal::float2(6.8, -(t_11) * 0.048), blur);
    metal::float2 warpField = metal::float2(_e32.x, _e43.x);
    metal::float2 _e46 = q_4;
    float _e52 = u.warp;
    metal::float2 warped = _e46 + ((warpField - metal::float2(0.5)) * (0.28 + (_e52 * 0.17)));
    metal::float2 _e70 = lqFbm((warped * 1.48) + metal::float2(t_11 * 0.032, -(t_11) * 0.02), blur * 1.48);
    metal::float2 _e81 = lqFbm((warped * 2.36) + metal::float2(3.1, -(t_11) * 0.024), blur * 2.36);
    float _e84 = u.sharp;
    float _e85 = lqRidgeS(_e81, _e84);
    float _e88 = lqStepS(_e70, 0.1, 0.9);
    float _e100 = u.ridgeAmt;
    float value_1 = metal::mix(_e88, metal::clamp((_e85 * 0.8) + (_e70.x * 0.46), 0.0, 1.0), _e100);
    metal::float4 _e104 = u.colorA;
    metal::float4 _e108 = u.colorB;
    metal::float4 _e112 = u.colorC;
    metal::float4 _e116 = u.colorD;
    metal::float3 _e118 = lqRamp(value_1, _e104.xyz, _e108.xyz, _e112.xyz, _e116.xyz, u);
    color_7 = _e118;
    metal::float3 _e120 = color_7;
    metal::float4 _e123 = u.colorA;
    color_7 = metal::mix(_e120, _e123.xyz, 0.08 * metal::smoothstep(0.62, 0.92, _e70.x));
    metal::float3 _e132 = color_7;
    metal::float3 _e133 = glsFinishPresetFluid(_e132, p_14, u);
    return _e133;
}

metal::float3 glsVoiceWaveFluid(
    metal::float2 p_15,
    float t_12,
    constant Uniforms& u
) {
    metal::float3 color_8 = {};
    float _e4 = u.zoom;
    float scale_3 = 0.76 + (_e4 * 0.34);
    metal::float2 q_9 = p_15 / metal::float2(scale_3);
    float rimEnvelope = metal::pow(metal::max(1.0 - (q_9.x * q_9.x), 0.0), 0.72);
    float drift_3 = t_12 * 0.82;
    float _e24 = u.warp;
    float amplitude_4 = 0.2 + (_e24 * 0.018);
    float mainY_2 = rimEnvelope * ((amplitude_4 * metal::sin((q_9.x * 1.48) + drift_3)) + (0.055 * metal::sin(((q_9.x * 3.2) - (drift_3 * 0.43)) + 1.1)));
    float distance = q_9.y - mainY_2;
    float _e52 = u.ridgeAmt;
    float width = 0.11 + ((1.0 - _e52) * 0.075);
    float membrane = metal::exp((-(distance) * distance) / metal::max(width * width, 0.001)) * rimEnvelope;
    float upperVeil = metal::exp((-(distance - 0.105) * (distance - 0.105)) / metal::max((width * width) * 2.4, 0.001)) * rimEnvelope;
    float lowerVeil = metal::exp((-(distance + 0.115) * (distance + 0.115)) / metal::max((width * width) * 2.8, 0.001)) * rimEnvelope;
    float crest = metal::exp((-(distance) * distance) / 0.0026) * rimEnvelope;
    float depth = metal::sqrt(metal::max(1.0 - metal::clamp(metal::dot(p_15, p_15), 0.0, 1.0), 0.0));
    metal::float4 _e112 = u.colorA;
    metal::float4 _e118 = u.colorD;
    color_8 = metal::mix(_e112.xyz * 0.7, _e118.xyz * 0.34, metal::smoothstep(-0.82, 0.82, q_9.y));
    metal::float3 _e128 = color_8;
    metal::float4 _e131 = u.colorB;
    color_8 = metal::mix(_e128, _e131.xyz, upperVeil * 0.7);
    metal::float3 _e136 = color_8;
    metal::float4 _e139 = u.colorC;
    color_8 = metal::mix(_e136, _e139.xyz, lowerVeil * 0.62);
    metal::float3 _e144 = color_8;
    metal::float4 _e147 = u.colorB;
    metal::float4 _e151 = u.colorC;
    color_8 = _e144 + ((metal::mix(_e147.xyz, _e151.xyz, 0.46) * membrane) * 0.34);
    metal::float3 _e159 = color_8;
    metal::float4 _e162 = u.highlightColor;
    color_8 = _e159 + ((_e162.xyz * crest) * 0.14);
    metal::float3 _e168 = color_8;
    color_8 = _e168 * (0.58 + (0.42 * depth));
    metal::float3 _e174 = color_8;
    metal::float3 _e175 = glsFinishPresetFluid(_e174, p_15, u);
    return _e175;
}

metal::float3 glsBlueDropFluid(
    metal::float2 p,
    float t,
    constant Uniforms& u
) {
    float depth = metal::sqrt(metal::max(1.0 - metal::clamp(metal::dot(p, p), 0.0, 1.0), 0.0));
    metal::float2 q = p * metal::mix(0.72, 1.0, depth * 0.62 + 0.38);
    q = glsRotate(q, -0.24 + 0.06 * metal::sin(t * 0.17));
    float scale = 1.0 + u.zoom * 1.12;
    float blur = 0.012 + 0.006 * u.zoom;
    metal::float2 driftA = lqFbm(q * 1.28 + metal::float2(t * 0.095, -t * 0.034), blur * 1.28);
    metal::float2 driftB = lqFbm(glsRotate(q, 1.08) * 1.62
                                 + metal::float2(-t * 0.042, t * 0.078), blur * 1.62);
    metal::float2 flowed = q + metal::float2(driftA.x - 0.5, driftB.x - 0.5)
                               * (0.24 + u.warp * 0.1);
    flowed.x += metal::sin(flowed.y * 2.15 + t * 0.24) * (0.035 + u.warp * 0.012);
    flowed.y += metal::sin(flowed.x * 1.38 - t * 0.18) * (0.045 + u.warp * 0.01);
    metal::float2 body = lqFbm(flowed * scale + metal::float2(t * 0.025, -t * 0.018), blur * scale);
    float marbleScale = 1.72 + u.zoom * 0.9;
    float marble = lqRidgeS(lqFbm(flowed * marbleScale
                                  + metal::float2(2.7, -t * 0.035), blur * marbleScale),
                            0.8 + u.sharp * 0.46);
    float value = metal::clamp(metal::mix(body.x, body.x * 0.62 + marble * 0.58, u.ridgeAmt), 0.0, 1.0);
    metal::float3 color = lqRamp(value, u.colorA.xyz, u.colorB.xyz, u.colorC.xyz, u.colorD.xyz, u);
    metal::float3 surface = metal::normalize(metal::float3(p.x, p.y, depth));
    metal::float3 direction = metal::normalize(metal::float3(-0.48, 0.62, 0.92));
    float light = metal::pow(metal::max(metal::dot(surface, direction), 0.0), 3.2);
    color = metal::mix(color, u.highlightColor.xyz, light * (0.035 + 0.05 * u.shade));
    color *= 0.74 + 0.26 * depth;
    return glsFinishPresetFluid(color, p, u);
}

metal::float3 glsVioletEmberFluid(
    metal::float2 p,
    float t,
    constant Uniforms& u
) {
    float scale = 1.08 + u.zoom * 1.18;
    float blur = 0.011 + 0.005 * u.zoom;
    float radius = metal::length(p);
    float twist = t * 0.055 + radius * (0.72 + u.warp * 0.11)
                  + 0.08 * metal::sin(t * 0.31 + radius * 4.0);
    metal::float2 q = glsRotate(p * scale, twist);
    metal::float2 low = lqFbm(q * 1.18 + metal::float2(t * 0.068, -t * 0.105), blur * 1.18);
    metal::float2 cross = lqFbm(glsRotate(q, -1.12) * 1.52
                                + metal::float2(-t * 0.094, t * 0.042)
                                + metal::float2(low.x * 1.35, -low.x * 0.72), blur * 1.52);
    metal::float2 warped = q + metal::float2(low.x - 0.5, cross.x - 0.5)
                              * (0.3 + u.warp * 0.12);
    metal::float2 melt = lqFbm(warped * 1.34
                               + metal::float2(cross.x * 1.48, low.x * 1.12), blur * 1.34);
    float veinScale = 2.05 + u.zoom * 0.72;
    float veins = lqRidgeS(lqFbm(warped * veinScale
                                 + metal::float2(-2.1, t * 0.052), blur * veinScale),
                           0.82 + u.sharp * 0.58);
    float heat = metal::smoothstep(0.18, 0.92,
                                   melt.x * (0.72 - u.ridgeAmt * 0.16)
                                   + veins * (0.32 + u.ridgeAmt * 0.5));
    metal::float3 color = lqRamp(heat, u.colorA.xyz, u.colorB.xyz, u.colorC.xyz, u.colorD.xyz, u);
    float pulse = 0.94 + 0.06 * metal::sin(t * 0.44 + melt.x * 5.0);
    color *= pulse;
    color = metal::mix(color, u.highlightColor.xyz, metal::pow(veins, 4.0) * 0.045);
    return glsFinishPresetFluid(color, p, u);
}

metal::float3 glsRefractiveBlobFluid(
    metal::float2 p,
    float t,
    constant Uniforms& u
) {
    float radial2 = metal::clamp(metal::dot(p, p), 0.0, 1.0);
    float depth = metal::sqrt(metal::max(1.0 - radial2, 0.0));
    float scale = 0.82 + u.zoom * 1.08;
    float blur = 0.012 + 0.005 * u.zoom;
    metal::float2 q = glsRotate(p * scale, 0.08 * metal::sin(t * 0.17));
    metal::float2 driftA = lqFbm(
        q * 1.16 + metal::float2(t * 0.052, -t * 0.078), blur * 1.16);
    metal::float2 driftB = lqFbm(
        glsRotate(q, 1.21) * 1.34 + metal::float2(-t * 0.064, t * 0.041),
        blur * 1.34);
    q += metal::float2(driftA.x - 0.5, driftB.x - 0.5)
       * (0.34 + u.warp * 0.105);

    metal::float2 body = lqFbm(
        q * 1.42 + metal::float2(driftB.x * 0.82, driftA.x * 0.66),
        blur * 1.42);
    float ribbonPhase = q.y * (2.2 + u.warp * 0.11)
                      + metal::sin(q.x * 1.72 - t * 0.19) * 0.92
                      + metal::sin((q.x + q.y) * 1.08 + t * 0.13) * 0.46;
    float ribbon = metal::pow(
        metal::clamp(1.0 - metal::abs(metal::sin(ribbonPhase)), 0.0, 1.0),
        0.82 + u.sharp * 0.23);
    float fold = lqRidgeS(
        lqFbm(q * 2.05 + metal::float2(2.8, -t * 0.037), blur * 2.05),
        0.9 + u.sharp * 0.32);
    float value = metal::clamp(
        body.x * 0.5 + driftA.x * 0.16
        + ribbon * (0.2 + u.ridgeAmt * 0.2)
        + fold * u.ridgeAmt * 0.18, 0.0, 1.0);

    metal::float3 color = lqRamp(
        value, u.colorA.xyz, u.colorB.xyz, u.colorC.xyz, u.colorD.xyz, u);
    float caustic = metal::pow(ribbon, 3.1) * (0.24 + 0.28 * u.ridgeAmt)
                  + metal::pow(fold, 4.2) * 0.08;
    color = metal::mix(color, u.colorD.xyz, metal::clamp(caustic, 0.0, 0.52));
    color *= 0.7 + depth * 0.3;
    float key = metal::pow(metal::max(metal::dot(
        metal::normalize(metal::float3(p, depth)),
        metal::normalize(metal::float3(-0.42, 0.58, 0.9))), 0.0), 4.0);
    color = metal::mix(color, u.highlightColor.xyz, key * 0.055);
    return glsFinishPresetFluid(color, p, u);
}

metal::float3 glsParticleRibbonFluid(
    metal::float2 p,
    float t,
    constant Uniforms& u
) {
    return metal::float3(0.0);
}

metal::float3 glsPresetFluid(
    metal::float2 p_16,
    int style,
    float t_13,
    constant Uniforms& u
) {
    if (style == 9) {
        metal::float3 _e5 = glsSiriFluid(p_16, t_13, u);
        return _e5;
    }
    if (style == 10) {
        metal::float3 _e8 = glsAuroraFluid(p_16, t_13, u);
        return _e8;
    }
    if (style == 11) {
        metal::float3 _e11 = glsPlasmaFluid(p_16, t_13, u);
        return _e11;
    }
    if (style == 12) {
        metal::float3 _e14 = glsChromeFluid(p_16, t_13, u);
        return _e14;
    }
    if (style == 13) {
        metal::float3 _e17 = glsOpalFluid(p_16, t_13, u);
        return _e17;
    }
    if (style == 14) {
        metal::float3 _e20 = glsSpectrumFluid(p_16, t_13, u);
        return _e20;
    }
    if (style == 15) {
        metal::float3 _e23 = glsFrostFluid(p_16, t_13, u);
        return _e23;
    }
    if (style == 19) {
        metal::float3 _e26 = glsVoiceWaveFluid(p_16, t_13, u);
        return _e26;
    }
    if (style == 20) {
        return glsBlueDropFluid(p_16, t_13, u);
    }
    if (style == 21) {
        return glsVioletEmberFluid(p_16, t_13, u);
    }
    if (style == 22) {
        return glsChromaticMetalFluid(p_16, t_13, u);
    }
    if (style == 23) {
        return glsRefractiveBlobFluid(p_16, t_13, u);
    }
    if (style == 24) {
        return glsParticleRibbonFluid(p_16, t_13, u);
    }
    metal::float3 _e27 = glsFrostFluid(p_16, t_13, u);
    return _e27;
}

metal::float3 glsFluid(
    metal::float2 fu,
    int md,
    float t_14,
    constant Uniforms& u
) {
    metal::float3 fcol = {};
    metal::float2 pp = {};
    float v_2 = {};
    float df = metal::length(fu);
    metal::float4 _e6 = u.colorA;
    metal::float3 cA_1 = _e6.xyz;
    metal::float4 _e10 = u.colorB;
    metal::float3 cB_1 = _e10.xyz;
    metal::float4 _e14 = u.colorC;
    metal::float3 cC_1 = _e14.xyz;
    metal::float4 _e18 = u.colorD;
    metal::float3 cD_1 = _e18.xyz;
    float _e24 = u.glassEnabled;
    float blurSigma = (_e24 > 0.5) ? GL_BSIG_GLASS : GL_BSIG_CLEAR;
    float _e30 = u.zoom;
    float sp = blurSigma * _e30;
    float sw = (sp * 1.1) * GL_KWA;
    if (md < 0) {
        float _e41 = u.zoom;
        pp = fu * _e41;
        float _e46 = pp.y;
        pp.y = _e46 + (t_14 * 0.05);
        metal::float2 _e50 = pp;
        metal::float2 _e58 = lqFbm((_e50 * 1.1) + metal::float2(0.0, t_14 * 0.09), sw);
        metal::float2 _e60 = pp;
        metal::float2 _e69 = lqFbm((_e60 * 1.1) + metal::float2(7.7, -(t_14) * 0.07), sw);
        metal::float2 w = metal::float2(_e58.x, _e69.x);
        metal::float2 _e72 = pp;
        float _e75 = u.warp;
        metal::float2 q_10 = _e72 + (_e75 * (w - metal::float2(0.5)));
        metal::float2 _e90 = lqFbm((q_10 * 1.5) + metal::float2(t_14 * 0.04, 0.0), sp * 1.5);
        metal::float2 _e98 = lqFbm((q_10 * 2.2) + metal::float2(3.1), sp * 2.2);
        float _e101 = u.sharp;
        float _e102 = lqRidgeS(_e98, _e101);
        float _e105 = lqStepS(_e90, 0.12, 0.88);
        float _e117 = u.ridgeAmt;
        float v_3 = metal::mix(_e105, metal::clamp((_e102 * 0.85) + (0.45 * _e90.x), 0.0, 1.0), _e117);
        metal::float3 _e119 = lqRamp(v_3, cA_1, cB_1, cC_1, cD_1, u);
        fcol = _e119;
    } else {
        float _e122 = u.zoom;
        metal::float2 pp_1 = fu * _e122;
        metal::float2 _e131 = lqFbm((pp_1 * 1.1) + metal::float2(0.0, t_14 * 0.09), sw);
        metal::float2 _e141 = lqFbm((pp_1 * 1.1) + metal::float2(7.7, -(t_14) * 0.07), sw);
        metal::float2 w_1 = metal::float2(_e131.x, _e141.x);
        float _e146 = u.warp;
        metal::float2 q_11 = pp_1 + (_e146 * (w_1 - metal::float2(0.5)));
        if (md == 0) {
            metal::float2 _e158 = lqFbm(q_11 * 2.2, sp * 2.2);
            float damp = metal::exp(((-18.0 * _e158.y) * _e158.y) - ((24.5 * sp) * sp));
            v_2 = 0.5 + ((0.5 * damp) * metal::sin(((q_11.x * 7.0) + (_e158.x * 6.0)) + (t_14 * 0.35)));
            float _e186 = v_2;
            metal::float2 _e195 = lqFbm((q_11 * 1.4) + metal::float2(t_14 * 0.03), sp * 1.4);
            v_2 = metal::mix(_e186, _e195.x, 0.25);
            float _e199 = v_2;
            metal::float3 _e200 = lqRamp(_e199, cA_1, cB_1, cC_1, cD_1, u);
            fcol = _e200;
        } else {
            if (md == 1) {
                metal::float2 _e212 = lqFbm((q_11 * 1.4) + metal::float2(t_14 * 0.06, 0.0), sp * 1.4);
                float _e215 = u.sharp;
                float _e216 = lqRidgeS(_e212, _e215);
                metal::float2 _e226 = lqFbm((q_11 * 1.7) - metal::float2(0.0, t_14 * 0.05), sp * 1.7);
                float _e229 = u.sharp;
                float _e230 = lqRidgeS(_e226, _e229);
                float v_4 = _e216 * _e230;
                metal::float3 _e234 = lqRamp(metal::pow(v_4, 0.7), cA_1, cB_1, cC_1, cD_1, u);
                fcol = _e234;
            } else {
                if (md == 6) {
                    metal::float2 _e247 = lqFbm((q_11 * 2.6) + metal::float2(t_14 * 0.025), sp * 2.6);
                    metal::float2 _e255 = lqFbm((q_11 * 1.3) + metal::float2(1.5 * _e247.x), sp * 1.3);
                    metal::float2 _e263 = lqFbm((q_11 * 2.1) + metal::float2(7.0), sp * 2.1);
                    float _e265 = lqRidgeS(_e263, 1.3);
                    float _e268 = lqStepS(_e255, 0.1, 0.9);
                    metal::float3 _e269 = lqRamp(_e268, cA_1, cB_1, cC_1, cD_1, u);
                    fcol = _e269;
                    metal::float3 _e270 = fcol;
                    fcol = _e270 * (1.0 - (0.18 * _e265));
                } else {
                    metal::float2 q2_ = q_11 + metal::float2(0.0, -(t_14) * 0.14);
                    metal::float2 _e294 = lqFbm((q2_ * 2.4) + metal::float2(0.0, -(t_14) * 0.05), sp * 2.4);
                    metal::float2 _e302 = lqFbm((q2_ * 1.6) + metal::float2(2.2 * _e294.x), sp * 1.6);
                    float _e304 = lqPowS(_e302, 1.5);
                    metal::float3 _e305 = lqRamp(_e304, cA_1, cB_1, cC_1, cD_1, u);
                    fcol = _e305;
                }
            }
        }
    }
    metal::float3 _e306 = fcol;
    metal::float4 _e309 = u.highlightColor;
    float _e313 = u.shade;
    fcol = metal::mix(_e306, _e309.xyz, (_e313 * 0.3) * metal::smoothstep(0.25, 1.25, metal::dot(fu, metal::float2(-0.32, 0.78))));
    metal::float3 _e325 = fcol;
    float _e328 = u.shade;
    fcol = _e325 * (1.0 - ((_e328 * 0.42) * metal::smoothstep(-0.05, 1.25, metal::dot(fu, metal::float2(0.45, -0.62)))));
    metal::float3 _e342 = fcol;
    float _e345 = u.shade;
    fcol = _e342 * (1.0 - ((_e345 * 0.3) * metal::smoothstep(0.72, 1.0, df)));
    metal::float3 _e355 = fcol;
    return metal::clamp(_e355, metal::float3(0.0), metal::float3(1.0));
}

metal::float3 glsOver(
    metal::float3 dst,
    metal::float3 src,
    float a_3
) {
    float k_5 = metal::clamp(a_3, 0.0, 1.0);
    return (src * k_5) + (dst * (1.0 - k_5));
}

float glsRefractionProfile(
    float t_15
) {
    float depth_1 = metal::clamp(t_15, 0.0, 1.0);
    float circular = metal::sqrt(metal::max(1.0 - ((1.0 - depth_1) * (1.0 - depth_1)), 0.0));
    return 1.0 - circular;
}

float glsHighlightLobe(
    metal::float2 normal,
    metal::float2 direction,
    float cut,
    float power
) {
    float angular = metal::clamp((metal::dot(normal, direction) - cut) / metal::max(1.0 - cut, 0.001), 0.0, 1.0);
    return metal::pow(angular, power);
}

int naga_f2i32(float value) {
    return static_cast<int>(metal::clamp(value, -2147483600.0, 2147483500.0));
}

metal::float2 glsContourWave(
    float angle_1,
    float t_16,
    constant Uniforms& u
) {
    float _e4 = u.style;
    int style_1 = naga_f2i32(_e4 + 0.5);
    if (style_1 == 19) {
        float wave_1 = (metal::sin((angle_1 * 2.0) + (t_16 * 0.27)) * 0.72) + (metal::sin(((angle_1 * 4.0) - (t_16 * 0.16)) + 2.1) * 0.28);
        float slope = (metal::cos((angle_1 * 2.0) + (t_16 * 0.27)) * 1.44) + (metal::cos(((angle_1 * 4.0) - (t_16 * 0.16)) + 2.1) * 1.12);
        return metal::float2(wave_1, slope);
    }
    float wave_2 = ((metal::sin((angle_1 * 3.0) + (t_16 * 0.62)) * 0.52) + (metal::sin(((angle_1 * 5.0) - (t_16 * 0.41)) + 1.7) * 0.31)) + (metal::sin(((angle_1 * 2.0) + (t_16 * 0.23)) + 3.1) * 0.17);
    float slope_1 = ((metal::cos((angle_1 * 3.0) + (t_16 * 0.62)) * 1.56) + (metal::cos(((angle_1 * 5.0) - (t_16 * 0.41)) + 1.7) * 1.55)) + (metal::cos(((angle_1 * 2.0) + (t_16 * 0.23)) + 3.1) * 0.34);
    return metal::float2(wave_2, slope_1);
}

float glsContourStrength(
    constant Uniforms& u
) {
    float _e2 = u.style;
    if (_e2 >= 18.5) {
        return 0.11;
    }
    float _e10 = u.style;
    return (_e10 >= 15.5) ? 0.16 : 0.09;
}

float glsContourScale(
    metal::float2 uv_1,
    float t_17,
    float amount,
    constant Uniforms& u
) {
    if (amount <= 0.0) {
        return 1.0;
    }
    metal::float2 _e9 = glsContourWave(metal::atan2(uv_1.y, uv_1.x), t_17, u);
    float _e13 = glsContourStrength(u);
    return 1.0 + ((metal::clamp(amount, 0.0, 1.0) * _e13) * _e9.x);
}

metal::float2 glsContourNormal(
    metal::float2 uv_2,
    float rad_1,
    float t_18,
    float amount_1,
    constant Uniforms& u
) {
    float distance_1 = metal::length(uv_2);
    if (distance_1 <= 0.0001) {
        return metal::float2(0.0);
    }
    metal::float2 radial = uv_2 / metal::float2(distance_1);
    metal::float2 _e14 = glsContourWave(metal::atan2(uv_2.y, uv_2.x), t_18, u);
    float _e18 = glsContourStrength(u);
    float slope_2 = (metal::clamp(amount_1, 0.0, 1.0) * _e18) * _e14.y;
    metal::float2 tangent = metal::float2(-(radial.y), radial.x);
    return metal::normalize(radial - (tangent * ((rad_1 * slope_2) / distance_1)));
}

metal::float2 glsRefractionNormal(
    metal::float2 base,
    metal::float2 p,
    float t,
    int style
) {
    if (style != 23) {
        return base;
    }
    metal::float2 tangent = metal::float2(-base.y, base.x);
    float a = lqFbm(
        p * 2.15 + metal::float2(t * 0.061, -t * 0.043), 0.018).x;
    float b = lqFbm(
        glsRotate(p, 1.37) * 2.55 + metal::float2(-t * 0.037, t * 0.052),
        0.021).x;
    float wave = (a - b) * 0.76
               + metal::sin(metal::atan2(p.y, p.x) * 3.0 + t * 0.21) * 0.08;
    return metal::normalize(base + tangent * wave);
}

metal::float4 orbGlassLiquidAnim(
    metal::float2 uv01_,
    constant Uniforms& u
) {
    metal::float2 fc = metal::float2(uv01_.x, 1.0 - uv01_.y) * u.size;
    metal::float2 uv = (2.0 * fc - u.size)
                     / metal::max(metal::min(u.size.x, u.size.y), 1.0);
    float rad = metal::max(u.radius, 0.05);
    float t = u.time * u.speed;
    int s = naga_f2i32(u.style + 0.5);
    bool emissionOnly = u.glassEnabled <= 0.5 && (s == 9 || s == 14 || s == 24);
    float contourRad = rad * glsContourScale(uv, t, u.contourDeform, u);

    if (metal::length(uv) > contourRad * (1.01 + mfEdgeD(u.edgeSoftness))) {
        metal::float3 halo = mfEdgeGlow(metal::float3(0.0), uv, metal::float2(0.0),
                                         contourRad, u.edgeSoftness, u.edgeGlow,
                                         u.glowColor.xyz);
        halo = metal::clamp(halo, metal::float3(0.0), metal::float3(1.0));
        float haloAlpha = metal::max(halo.x, metal::max(halo.y, halo.z));
        return metal::float4(halo, haloAlpha);
    }

    metal::float2 p = uv / contourRad;
    float pd = metal::length(p);
    metal::float2 fu = p / GL_FU;
    int md = -1;
    if (s == 1) { md = 1; }
    else if (s == 3 || s == 8) { md = 7; }
    else if (s == 5) { md = 6; }
    else if (s == 7) { md = 0; }

    float clearFa = 1.0 - metal::smoothstep(GL_CLEAR_EA, GL_CLEAR_EB, pd);
    metal::float2 contourNormal = glsContourNormal(uv, rad, t, u.contourDeform, u);
    metal::float2 normal = glsRefractionNormal(contourNormal, p, t, s);
    float edgeDepth = metal::max(1.0 - pd, 0.0);
    float refractionWidth = 0.015 + 0.95 * metal::clamp(u.shellMidAlpha, 0.0, 1.0);
    float refractionT = edgeDepth / metal::max(refractionWidth, 0.001);
    float refractionProfile = metal::pow(glsRefractionProfile(refractionT), 0.68);
    float refractionAmount = 1.6 * metal::clamp(u.glassOpacity, 0.0, 1.0)
                           * refractionProfile;
    metal::float2 refractedP = p - normal * refractionAmount;
    metal::float3 fcol = metal::float3(0.0);

    if (clearFa > 0.0) {
        if (s >= 9) {
            if (u.glassEnabled > 0.5) {
                float channelSplit = 0.14 * metal::clamp(u.gloss, 0.0, 2.0)
                                   * metal::clamp(u.glassOpacity, 0.0, 1.0)
                                   * refractionProfile;
                metal::float3 redSample = glsPresetFluid(refractedP - normal * channelSplit, s, t, u);
                metal::float3 greenSample = glsPresetFluid(refractedP, s, t, u);
                metal::float3 blueSample = glsPresetFluid(refractedP + normal * channelSplit, s, t, u);
                fcol = metal::float3(redSample.x, greenSample.y, blueSample.z);
            } else {
                fcol = glsPresetFluid(p, s, t, u);
            }
        } else {
            fcol = glsFluid(fu, md, t, u);
        }
    }

    float lum = metal::dot(fcol, metal::float3(0.213, 0.715, 0.072));
    metal::float3 clearSat = metal::clamp(
        metal::float3(lum) + (fcol - metal::float3(lum)) * 1.22,
        metal::float3(0.0), metal::float3(1.0));
    bool particleGlassOverlay = s == 24;
    metal::float3 col = particleGlassOverlay
        ? metal::float3(0.0)
        : glsOver(u.canvasColor.xyz, clearSat, 0.99 * clearFa);
    if (emissionOnly) {
        float signal = metal::max(clearSat.x, metal::max(clearSat.y, clearSat.z));
        float emissionCoverage = metal::smoothstep(0.025, 0.16, signal);
        col = clearSat * emissionCoverage;
    }

    if (u.glassEnabled > 0.5) {
        float surfaceWidth = particleGlassOverlay
            ? 0.09 + 0.12 * metal::clamp(u.shellEdgeAlpha, 0.0, 1.0)
            : 0.026 + 0.055 * metal::clamp(u.shellEdgeAlpha, 0.0, 1.0);
        float surfaceBand = (1.0 - metal::smoothstep(0.0, surfaceWidth, edgeDepth)) * clearFa;
        float opticalRim = metal::pow(surfaceBand, particleGlassOverlay ? 1.3 : 1.8);
        float innerRimAlpha = !particleGlassOverlay
            ? opticalRim * u.glassOpacity * 0.45
            : opticalRim * u.glassOpacity * 0.14;
        col = glsOver(col, u.shellInner.xyz, innerRimAlpha);

        metal::float2 coolDirection = metal::normalize(metal::float2(0.84, 0.54));
        metal::float2 warmDirection = metal::normalize(metal::float2(-0.62, -0.78));
        float coolSplit = glsHighlightLobe(normal, coolDirection, -0.32, 1.8);
        float warmSplit = glsHighlightLobe(normal, warmDirection, -0.28, 2.0);
        float dispersion = opticalRim * metal::clamp(u.gloss, 0.0, 2.0)
                         * (0.8 + 0.8 * u.shellEdgeAlpha);
        col = glsOver(col, u.shellMid.xyz, dispersion * coolSplit);
        col = glsOver(col, u.shellEdge.xyz, dispersion * warmSplit);

        float edgeShadow = opticalRim * (0.015 + 0.15 * u.shellEdgeAlpha)
                         * (0.15 + 0.85 * metal::max(
                            metal::dot(normal, metal::float2(0.45, -0.89)), 0.0));
        col *= 1.0 - edgeShadow;

        metal::float2 keyDirection = metal::normalize(metal::float2(-0.68, 0.73));
        metal::float2 fillDirection = metal::normalize(metal::float2(0.74, -0.67));
        float key = opticalRim * glsHighlightLobe(normal, keyDirection, 0.2, 2.8)
                  * metal::clamp(u.sheen, 0.0, 2.0) * 1.4;
        float fill = opticalRim * glsHighlightLobe(normal, fillDirection, 0.4, 3.6)
                   * metal::clamp(u.sheen, 0.0, 2.0) * 1.0;
        col = glsOver(col, u.sheenColor.xyz, key);
        col = glsOver(col, u.specColor.xyz, fill);
    }

    float ballA = 1.0 - metal::smoothstep(
        0.99 - mfEdgeD(u.edgeSoftness),
        1.01 + mfEdgeD(u.edgeSoftness), pd);
    col = metal::clamp(col * metal::max(u.exposure, 0.0),
                       metal::float3(0.0), metal::float3(1.0)) * ballA;
    metal::float3 edged = mfEdgeGlow(col, uv, metal::float2(0.0), contourRad,
                                     u.edgeSoftness, u.edgeGlow, u.glowColor.xyz);
    metal::float3 finalColor = metal::clamp(
        edged, metal::float3(0.0), metal::float3(1.0));
    float emissionAlpha = metal::max(finalColor.x, metal::max(finalColor.y, finalColor.z));
    float sphereAlpha = metal::clamp(metal::max(ballA, emissionAlpha), 0.0, 1.0);
    float finalAlpha = (emissionOnly || particleGlassOverlay)
        ? emissionAlpha
        : sphereAlpha;
    return metal::float4(finalColor, finalAlpha);
}

struct vs_mainInput {
};
struct vs_mainOutput {
    metal::float4 pos [[position]];
    metal::float2 uv [[user(loc0), center_perspective]];
};
vertex vs_mainOutput vs_main(
  uint i [[vertex_id]]
) {
    type_7 p = type_7 {metal::float2(-1.0, -1.0), metal::float2(3.0, -1.0), metal::float2(-1.0, 3.0)};
    VOut out = {};
    metal::float2 _e15 = uint(i) < 3 ? p.inner[i] : DefaultConstructible();
    out.pos = metal::float4(_e15, 0.0, 1.0);
    metal::float2 _e20 = uint(i) < 3 ? p.inner[i] : DefaultConstructible();
    metal::float2 uv01_1 = (_e20 + metal::float2(1.0)) * 0.5;
    out.uv = metal::float2(uv01_1.x, 1.0 - uv01_1.y);
    VOut _e32 = out;
    const auto _tmp = _e32;
    return vs_mainOutput { _tmp.pos, _tmp.uv };
}


struct fs_mainInput {
    metal::float2 uv [[user(loc0), center_perspective]];
};
struct fs_mainOutput {
    metal::float4 member_1 [[color(0)]];
};
fragment fs_mainOutput fs_main(
  fs_mainInput varyings_1 [[stage_in]]
, metal::float4 pos [[position]]
, constant Uniforms& u [[buffer(0)]]
) {
    const VOut in = { pos, varyings_1.uv };
    metal::float4 _e2 = orbGlassLiquidAnim(in.uv, u);
    metal::float2 _e12 = u.size;
    metal::float2 fc_1 = metal::float2(in.uv.x, 1.0 - in.uv.y) * _e12;
    metal::float2 _e18 = u.size;
    float _e23 = u.size.x;
    float _e27 = u.size.y;
    metal::float2 uv_4 = ((2.0 * fc_1) - _e18) / metal::float2(metal::max(metal::min(_e23, _e27), 1.0));
    float _e35 = u.radius;
    float rad_3 = metal::max(_e35, 0.05);
    float _e40 = u.time;
    float _e43 = u.speed;
    float t_20 = _e40 * _e43;
    float _e47 = u.contourDeform;
    float _e48 = glsContourScale(uv_4, t_20, _e47, u);
    float contourRad_1 = rad_3 * _e48;
    metal::float2 _e76 = u.size;
    metal::float2 _e80 = u.size;
    metal::float2 q_12 = ((2.0 * fc_1) - _e76) / _e80;
    float fitEnd = 1.0;
    float fitFeather = 2.0 / metal::max(metal::min(u.size.x, u.size.y), 1.0);
    float fitStart = metal::min(metal::mix(contourRad_1, fitEnd, 0.5), fitEnd - fitFeather);
    float fit = 1.0 - metal::smoothstep(fitStart, fitEnd, metal::max(metal::abs(q_12.x), metal::abs(q_12.y)));
    return fs_mainOutput { metal::float4(_e2.xyz * fit, _e2.w * fit) };
}

constant uint PR_U_SEGMENTS = 384;
constant uint PR_V_SEGMENTS = 96;
constant uint PR_PARTICLES_PER_LAYER = PR_U_SEGMENTS * PR_V_SEGMENTS;

float prHash(float value) {
    return metal::fract(metal::sin(value * 12.9898 + 78.233) * 43758.5453);
}

metal::float3 prRotateX(metal::float3 p, float angle) {
    float c = metal::cos(angle);
    float s = metal::sin(angle);
    return metal::float3(p.x, c * p.y - s * p.z, s * p.y + c * p.z);
}

metal::float3 prRotateY(metal::float3 p, float angle) {
    float c = metal::cos(angle);
    float s = metal::sin(angle);
    return metal::float3(c * p.x + s * p.z, p.y, -s * p.x + c * p.z);
}

metal::float3 prCurve(
    float theta,
    float layer,
    float phase,
    constant Uniforms& u
) {
    float local = theta + layer * 0.11;
    float foldPhase = 2.0 * local + phase * (0.72 + layer * 0.025);
    float fold = metal::clamp(u.ribbonFold, 0.0, 1.2);
    float radial = 0.4 + (0.085 + fold * 0.04) * metal::cos(foldPhase);
    float orbit = local + phase * 0.13
                + metal::sin(local - phase * 0.22 + layer) * fold * 0.13;
    float vertical = (0.235 + fold * 0.085) * metal::sin(foldPhase)
                   + 0.055 * metal::sin(local * 3.0 - phase * 0.46 + layer * 0.7);
    return metal::float3(radial * metal::cos(orbit), vertical, radial * metal::sin(orbit));
}

metal::float3 prPalette(float valueIn, constant Uniforms& u) {
    float value = metal::fract(valueIn) * 4.0;
    if (value < 1.0) return metal::mix(u.colorA.xyz, u.colorB.xyz, value);
    if (value < 2.0) return metal::mix(u.colorB.xyz, u.colorC.xyz, value - 1.0);
    if (value < 3.0) return metal::mix(u.colorC.xyz, u.colorD.xyz, value - 2.0);
    return metal::mix(u.colorD.xyz, u.colorA.xyz, value - 3.0);
}

struct ribbon_vs_mainOutput {
    metal::float4 pos [[position]];
    metal::float2 local [[user(loc0), center_no_perspective]];
    metal::float3 color [[user(loc1), center_perspective]];
    float opacity [[user(loc2), center_perspective]];
};

vertex ribbon_vs_mainOutput ribbon_vs_main(
    uint vertexIndex [[vertex_id]],
    uint instanceIndex [[instance_id]],
    constant Uniforms& u [[buffer(0)]]
) {
    const metal::float2 corners[6] = {
        metal::float2(-1.0, -1.0), metal::float2(1.0, -1.0),
        metal::float2(-1.0, 1.0), metal::float2(-1.0, 1.0),
        metal::float2(1.0, -1.0), metal::float2(1.0, 1.0)
    };
    uint layerIndex = instanceIndex / PR_PARTICLES_PER_LAYER;
    uint particleIndex = instanceIndex % PR_PARTICLES_PER_LAYER;
    uint uIndex = particleIndex / PR_V_SEGMENTS;
    uint vIndex = particleIndex % PR_V_SEGMENTS;
    float layer = float(layerIndex);
    float random = prHash(float(instanceIndex));
    bool activeLayer = layer < metal::floor(metal::clamp(u.ribbonCount, 2.0, 6.0) + 0.5);

    float uCoord = (float(uIndex) + prHash(float(instanceIndex) + 11.0) * 0.56)
                 / float(PR_U_SEGMENTS);
    float vCoord = (float(vIndex) + prHash(float(instanceIndex) + 29.0) * 0.46)
                 / float(PR_V_SEGMENTS);
    float strip = vCoord * 2.0 - 1.0;
    float t = u.time * u.speed;
    float phase = t * 0.48;
    float arc = metal::fract(uCoord + layer * 0.211 - phase * 0.019);
    float arcLength = 0.76 + 0.055 * metal::sin(t * 0.23 + layer * 1.71);
    float arcPosition = arc / arcLength;
    float arcEnvelope = metal::smoothstep(0.0, 0.075, arcPosition)
                      * (1.0 - metal::smoothstep(0.88, 1.0, arcPosition));
    bool active = activeLayer
               && arc <= arcLength
               && random <= metal::clamp(u.particleDensity, 0.2, 1.0);
    float theta = uCoord * 6.28318530718;
    metal::float3 center = prCurve(theta, layer, phase, u);
    metal::float3 ahead = prCurve(theta + 0.006, layer, phase, u);
    metal::float3 tangent = metal::normalize(ahead - center);
    metal::float3 radial = metal::normalize(center + metal::float3(0.001, 0.013, 0.007));
    metal::float3 side = metal::normalize(metal::cross(tangent, radial));
    metal::float3 surfaceNormal = metal::normalize(metal::cross(side, tangent));
    float twist = theta * (0.72 + u.ribbonTwist * 0.58)
                + phase * 0.74 + layer * 1.17;
    metal::float3 ribbonDirection = metal::normalize(
        side * metal::cos(twist) + surfaceNormal * metal::sin(twist));
    float widthEnvelope = (0.72 + 0.28
        * metal::pow(metal::sin(theta * 1.5 + phase + layer), 2.0))
        * metal::mix(0.42, 1.0, metal::sqrt(metal::max(arcEnvelope, 0.0)));
    metal::float3 position = center
        + ribbonDirection * strip * u.ribbonWidth * 0.5 * widthEnvelope;

    float pulse = metal::sin(t * 0.73 + layer * 1.71)
                + 0.44 * metal::sin(t * 1.17 + layer * 0.83 + 1.2);
    position *= 1.0 + u.ribbonBreath * pulse * 0.16;
    float layerCenter = layer
        - (metal::floor(metal::clamp(u.ribbonCount, 2.0, 6.0) + 0.5) - 1.0) * 0.5;
    position = prRotateY(
        position, layerCenter * 0.24 + metal::sin(t * 0.19 + layer * 1.3) * 0.055);
    position = prRotateX(
        position, layerCenter * 0.14 + metal::cos(t * 0.17 + layer * 0.9) * 0.04);
    position = prRotateY(position, t * 0.105 + metal::sin(t * 0.21) * 0.11);
    position = prRotateX(position, -0.2 + metal::sin(t * 0.16 + layer * 0.1) * 0.16);

    float minSize = metal::max(metal::min(u.size.x, u.size.y), 1.0);
    float depthScale = 0.88 + position.z * 0.16;
    metal::float2 orbPosition = position.xy * u.radius * 1.45 * depthScale;
    metal::float2 clip = metal::float2(
        orbPosition.x * minSize / metal::max(u.size.x, 1.0),
        orbPosition.y * minSize / metal::max(u.size.y, 1.0));
    float canvasParticleScale = metal::clamp(minSize / 640.0, 0.22, 1.0);
    float pointPixels = metal::max(0.6, u.particleSize)
                      * (1.5 + u.particleBloom * 2.5)
                      * (0.92 + position.z * 0.18)
                      * canvasParticleScale;
    metal::float2 corner = corners[vertexIndex];
    metal::float2 pointOffset = corner * pointPixels * 2.0
                              / metal::max(u.size, metal::float2(1.0));

    float colorPhase = uCoord * 0.32 + layer * 0.19 + phase * 0.025
                     + position.z * 0.08;
    float stripEdge = metal::smoothstep(0.58, 1.0, metal::abs(strip));
    float front = metal::clamp(0.78 + position.z * 0.54, 0.5, 1.24);
    float baseOpacity = metal::mix(0.025, 0.009,
        metal::clamp(u.shade / 1.5, 0.0, 1.0));

    ribbon_vs_mainOutput out;
    out.pos = active
        ? metal::float4(clip + pointOffset,
                        metal::clamp(0.5 - position.z * 0.12, 0.05, 0.95), 1.0)
        : metal::float4(2.0, 2.0, 1.0, 1.0);
    out.local = corner;
    out.color = metal::pow(
        metal::mix(prPalette(colorPhase, u), u.highlightColor.xyz, stripEdge * 0.56),
        metal::float3(0.72)) * front;
    out.opacity = active
        ? baseOpacity
            * (0.72 + stripEdge * 1.28)
            * arcEnvelope
            * metal::pow(canvasParticleScale, 1.35)
        : 0.0;
    return out;
}

struct ribbon_fs_mainOutput {
    metal::float4 color [[color(0)]];
};

fragment ribbon_fs_mainOutput ribbon_fs_main(
    ribbon_vs_mainOutput in [[stage_in]],
    constant Uniforms& u [[buffer(0)]]
) {
    float distanceSquared = metal::dot(in.local, in.local);
    if (distanceSquared > 1.0) discard_fragment();
    float core = metal::exp(-distanceSquared * 4.8);
    float halo = metal::exp(-distanceSquared * 1.35);
    float bloom = metal::clamp(u.particleBloom, 0.0, 2.0);
    float intensity = in.opacity * (core * 1.9 + halo * bloom * 0.72)
                    * metal::max(u.exposure, 0.0);
    float glowMix = metal::clamp((halo - core * 0.45)
        * (0.18 + u.edgeGlow * 0.5), 0.0, 0.7);
    metal::float3 color = metal::mix(in.color, u.glowColor.xyz, glowMix);
    float alpha = metal::clamp(intensity, 0.0, 1.0);
    return ribbon_fs_mainOutput { metal::float4(color * alpha, alpha) };
}

metal::float2 prTextureUvFromOrb(
    metal::float2 p,
    float contourRad,
    constant Uniforms& u
) {
    float minSize = metal::max(metal::min(u.size.x, u.size.y), 1.0);
    metal::float2 fc = (p * contourRad * minSize + u.size) * 0.5;
    return metal::clamp(
        metal::float2(
            fc.x / metal::max(u.size.x, 1.0),
            1.0 - fc.y / metal::max(u.size.y, 1.0)),
        metal::float2(0.0),
        metal::float2(1.0));
}

struct ribbon_composite_fs_mainOutput {
    metal::float4 color [[color(0)]];
};

fragment ribbon_composite_fs_mainOutput ribbon_composite_fs_main(
    fs_mainInput in [[stage_in]],
    metal::float4 position [[position]],
    constant Uniforms& u [[buffer(0)]],
    metal::texture2d<float> ribbonTexture [[texture(0)]]
) {
    constexpr metal::sampler ribbonSampler(
        metal::coord::normalized,
        metal::address::clamp_to_edge,
        metal::filter::linear);
    metal::float4 direct = ribbonTexture.sample(ribbonSampler, in.uv);
    if (u.glassEnabled <= 0.5) {
        return ribbon_composite_fs_mainOutput { direct };
    }

    metal::float2 fc = metal::float2(in.uv.x, 1.0 - in.uv.y) * u.size;
    float minSize = metal::max(metal::min(u.size.x, u.size.y), 1.0);
    metal::float2 uv = (2.0 * fc - u.size) / minSize;
    float rad = metal::max(u.radius, 0.05);
    float t = u.time * u.speed;
    float contourRad = rad * glsContourScale(uv, t, u.contourDeform, u);
    metal::float4 shell = orbGlassLiquidAnim(in.uv, u);
    if (metal::length(uv) > contourRad * (1.01 + mfEdgeD(u.edgeSoftness))) {
        return ribbon_composite_fs_mainOutput { shell };
    }

    metal::float2 p = uv / contourRad;
    float pd = metal::length(p);
    float clearFa = 1.0 - metal::smoothstep(GL_CLEAR_EA, GL_CLEAR_EB, pd);
    metal::float2 normal = glsContourNormal(uv, rad, t, u.contourDeform, u);
    float edgeDepth = metal::max(1.0 - pd, 0.0);
    float refractionWidth = 0.015 + 0.95 * metal::clamp(u.shellMidAlpha, 0.0, 1.0);
    float refractionT = edgeDepth / metal::max(refractionWidth, 0.001);
    float refractionProfile = metal::pow(glsRefractionProfile(refractionT), 0.68);
    float refractionAmount = 1.6 * metal::clamp(u.glassOpacity, 0.0, 1.0)
                           * refractionProfile;
    metal::float2 refractedP = p - normal * refractionAmount;
    float channelSplit = 0.14 * metal::clamp(u.gloss, 0.0, 2.0)
                       * metal::clamp(u.glassOpacity, 0.0, 1.0)
                       * refractionProfile;
    metal::float4 redSample = ribbonTexture.sample(
        ribbonSampler,
        prTextureUvFromOrb(refractedP - normal * channelSplit, contourRad, u));
    metal::float4 greenSample = ribbonTexture.sample(
        ribbonSampler,
        prTextureUvFromOrb(refractedP, contourRad, u));
    metal::float4 blueSample = ribbonTexture.sample(
        ribbonSampler,
        prTextureUvFromOrb(refractedP + normal * channelSplit, contourRad, u));
    float refractedAlpha = metal::max(
        redSample.w,
        metal::max(greenSample.w, blueSample.w)) * clearFa;
    metal::float4 refracted = metal::float4(
        metal::float3(redSample.x, greenSample.y, blueSample.z) * clearFa,
        refractedAlpha);
    return ribbon_composite_fs_mainOutput {
        metal::float4(
            shell.xyz + refracted.xyz * (1.0 - shell.w),
            shell.w + refracted.w * (1.0 - shell.w))
    };
}
`,Av={min:.3,max:.95},jv={glassEnabled:!0,speed:1,radius:.72,contourDeform:0,bandDensity:2,chromaticShift:.42,metalScale:.77,metalStretch:.23,metalAngle:65,metalOffset:0,metalPhase:0,metalEvolution:1,metalRoughness:.22,metalDepth:.25,particleDensity:.72,ribbonCount:5,ribbonWidth:.42,ribbonTwist:1.25,ribbonFold:.55,ribbonBreath:.3,particleSize:1.2,particleBloom:.7,zoom:.3,warp:3,ridgeAmt:.5,sharp:2.2,shade:.3,sheen:.36,gloss:.28,glassOpacity:.42,shellMidAlpha:.2,shellEdgeAlpha:.22,exposure:1,edgeSoftness:.005,edgeGlow:0,colorA:`#F7FBFF`,colorB:`#D6E8F7`,colorC:`#A8C8F0`,colorD:`#6F9EE8`,highlightColor:`#FFFFFF`,shellInner:`#FFFFFF`,shellMid:`#D6E8F7`,shellEdge:`#6F9EE8`,sheenColor:`#EAF4FF`,specColor:`#DCEAFF`,canvasColor:`#000000`,glowColor:`#6F9EE8`},Mv={siri:{...jv,speed:.82,zoom:.36,warp:3.2,ridgeAmt:.5,sharp:2.2,shade:.12,sheen:.28,gloss:.24,glassOpacity:.44,shellMidAlpha:.18,shellEdgeAlpha:.18,exposure:2,colorA:`#FFD86B`,colorB:`#82F4FF`,colorC:`#FF7BD5`,colorD:`#8E6CFF`,shellMid:`#9BF4FF`,shellEdge:`#C5A9FF`,canvasColor:`#030409`,glowColor:`#956CFF`},voiceWave:{...jv,speed:.95,radius:.7,contourDeform:.1,zoom:.36,warp:2.6,ridgeAmt:.46,shade:.08,sheen:.22,gloss:.36,glassOpacity:.48,shellMidAlpha:.18,shellEdgeAlpha:.2,exposure:1.35,colorA:`#09030E`,colorB:`#CE2CCB`,colorC:`#FF5C71`,colorD:`#7B53FF`,highlightColor:`#FFD9F0`,shellMid:`#E48BFF`,shellEdge:`#FF7890`,sheenColor:`#FFF1FA`,specColor:`#E7D9FF`,canvasColor:`#020105`,glowColor:`#CE2CCB`},aurora:{...jv,speed:3,contourDeform:.08,zoom:.4,warp:4.2,ridgeAmt:.62,sharp:2.1,shade:.18,exposure:1.18,colorA:`#030816`,colorB:`#20F0B6`,colorC:`#32A8FF`,colorD:`#A34BFF`,shellMid:`#32A8FF`,shellEdge:`#20F0B6`,canvasColor:`#010207`,glowColor:`#20F0B6`},plasma:{...jv,speed:1.32,contourDeform:.05,zoom:.55,warp:5.4,ridgeAmt:.78,sharp:4.2,shade:.16,exposure:1.25,colorA:`#06020E`,colorB:`#0099FF`,colorC:`#258BFF`,colorD:`#1375FF`,shellInner:`#FFFFFF`,shellMid:`#1951C2`,shellEdge:`#00E9FF`,sheenColor:`#EAF4FF`,specColor:`#DCEAFF`,canvasColor:`#020105`,glowColor:`#0099FF`},chrome:{...jv,speed:2,zoom:.36,warp:3.8,ridgeAmt:.44,sharp:5.2,shade:.58,exposure:1.08,colorA:`#FFFFFF`,colorB:`#B9C0CA`,colorC:`#343A43`,colorD:`#030405`,shellMid:`#B9C0CA`,shellEdge:`#FFFFFF`,canvasColor:`#050608`,glowColor:`#FFFFFF`},opal:{...jv,speed:1.5,zoom:.3,warp:2.8,ridgeAmt:.36,sharp:2,shade:.1,sheen:.3,gloss:.26,glassOpacity:.38,shellMidAlpha:.2,shellEdgeAlpha:.2,exposure:1.12,colorA:`#FFF6E8`,colorB:`#6EF2CF`,colorC:`#FF91D8`,colorD:`#756BFF`,shellMid:`#CDE5FF`,shellEdge:`#D9C8FF`,canvasColor:`#07080D`,glowColor:`#9E8CFF`},spectrum:{...jv,speed:1.8,contourDeform:.03,zoom:.46,warp:4.4,ridgeAmt:.72,shade:.06,sheen:.26,gloss:.24,glassOpacity:.4,shellMidAlpha:.18,shellEdgeAlpha:.18,exposure:1.5,colorA:`#FFFFFF`,colorB:`#1677FF`,colorC:`#F249A0`,colorD:`#35E6B2`,shellMid:`#66E8FF`,shellEdge:`#D26CFF`,canvasColor:`#03040A`,glowColor:`#1677FF`},frost:{...jv,speed:2.22,contourDeform:.04,zoom:.36,warp:3.7,ridgeAmt:.45,sharp:2.05,shade:.3,sheen:.34,gloss:.28,glassOpacity:.42,shellMidAlpha:.2,shellEdgeAlpha:.22,exposure:1,colorA:`#F7FBFF`,colorB:`#D6E8F7`,colorC:`#A8C8F0`,colorD:`#6F9EE8`,shellMid:`#D6E8F7`,shellEdge:`#6F9EE8`,canvasColor:`#000000`,glowColor:`#6F9EE8`},blueDrop:{...jv,speed:.9,radius:.74,contourDeform:.08,zoom:.48,warp:2.65,ridgeAmt:.42,sharp:2.4,shade:.16,sheen:.22,gloss:.42,glassOpacity:.66,shellMidAlpha:.32,shellEdgeAlpha:.24,exposure:1.24,colorA:`#020B1D`,colorB:`#0756B8`,colorC:`#1EC8FF`,colorD:`#DDFBFF`,highlightColor:`#EAFBFF`,shellInner:`#F6FDFF`,shellMid:`#4FD7FF`,shellEdge:`#466DFF`,sheenColor:`#DDFBFF`,specColor:`#A8D9FF`,canvasColor:`#010207`,glowColor:`#168DFF`},violetEmber:{...jv,speed:1.12,radius:.72,contourDeform:.04,zoom:.58,warp:4.7,ridgeAmt:.73,sharp:3.3,shade:.18,sheen:.2,gloss:.34,glassOpacity:.62,shellMidAlpha:.28,shellEdgeAlpha:.24,exposure:1.28,colorA:`#100016`,colorB:`#4A0E8F`,colorC:`#A52EFF`,colorD:`#F1A7FF`,highlightColor:`#FFD6FF`,shellInner:`#FCF5FF`,shellMid:`#C257FF`,shellEdge:`#6C2DFF`,sheenColor:`#F8E6FF`,specColor:`#D4B7FF`,canvasColor:`#030006`,glowColor:`#A52EFF`},refractiveBlob:{...jv,speed:.76,radius:.73,contourDeform:.16,zoom:.46,warp:3.65,ridgeAmt:.58,sharp:2.7,shade:.14,sheen:.14,gloss:.52,glassOpacity:.82,shellMidAlpha:.42,shellEdgeAlpha:.2,exposure:1.2,colorA:`#1B102B`,colorB:`#7056A8`,colorC:`#BFA5F5`,colorD:`#F1E8FF`,highlightColor:`#FFFFFF`,shellInner:`#F6F0FF`,shellMid:`#D9C7FF`,shellEdge:`#B59AE8`,sheenColor:`#FFFFFF`,specColor:`#E9DEFF`,canvasColor:`#050208`,glowColor:`#B18CFF`},particleRibbon:{...jv,glassEnabled:!0,speed:.72,radius:.66,particleDensity:1,ribbonCount:4,ribbonWidth:.48,ribbonTwist:1.15,ribbonFold:.6,ribbonBreath:.38,particleSize:1.12,particleBloom:1.22,shade:.12,sheen:.28,gloss:.24,glassOpacity:.44,shellMidAlpha:.18,shellEdgeAlpha:.18,exposure:1.48,colorA:`#63F1FF`,colorB:`#4A9DFF`,colorC:`#8566FF`,colorD:`#F15DE1`,highlightColor:`#F5FBFF`,shellInner:`#FFFFFF`,shellMid:`#9BF4FF`,shellEdge:`#C5A9FF`,sheenColor:`#EAF4FF`,specColor:`#DCEAFF`,canvasColor:`#010208`,glowColor:`#765CFF`},chromaticMetal:{...jv,speed:1.12,radius:.72,bandDensity:2,chromaticShift:.42,metalScale:.77,metalStretch:.23,metalAngle:65,metalOffset:0,metalPhase:0,metalEvolution:1,metalRoughness:.16,metalDepth:.38,shade:.1,sheen:.14,gloss:.46,glassOpacity:.54,shellMidAlpha:.2,shellEdgeAlpha:.16,exposure:1.08,colorA:`#FBFCFB`,colorB:`#7F8683`,colorC:`#D6DAD8`,colorD:`#33373A`,highlightColor:`#FFFFFF`,shellInner:`#F7FCFF`,shellMid:`#6EDCFF`,shellEdge:`#FF806D`,sheenColor:`#F7FCFF`,specColor:`#D9F3FF`,canvasColor:`#050606`,glowColor:`#BDEFFF`}},Nv=[`siri`,`voiceWave`,`particleRibbon`,`blueDrop`,`violetEmber`,`refractiveBlob`,`chromaticMetal`,`aurora`,`frost`,`chrome`,`opal`,`spectrum`,`plasma`],Pv={siri:9,voiceWave:19,aurora:10,plasma:11,chrome:12,opal:13,spectrum:14,frost:15,blueDrop:20,violetEmber:21,refractiveBlob:23,particleRibbon:24,chromaticMetal:22},Fv={style:`siri`,...Mv.siri};({...Fv});for(let e of Nv)if(!Number.isInteger(Pv[e]))throw Error(`预设缺少流场映射：${e}`);var Iv=[`#F7FBFF`,`#EFF6FD`,`#E0EEF9`,`#D4E6F7`,`#BBD5F3`,`#A6C7F0`,`#87B0EB`,`#6F9EE8`,`#6F9EE8`,`#6F9EE8`,`#6F9EE8`,`#6F9EE8`];function Lv(e){let t=e.slice(1);return[Number.parseInt(t.slice(0,2),16)/255,Number.parseInt(t.slice(2,4),16)/255,Number.parseInt(t.slice(4,6),16)/255,1]}function Rv(e,t,n,r,i){e.fill(0),e[0]=t,e[1]=n,e[2]=r,e.set([i.speed,i.radius,i.zoom,i.warp,i.ridgeAmt,i.sharp,i.shade,i.sheen,i.gloss,i.shellMidAlpha,i.shellEdgeAlpha,i.exposure,Pv[i.style],i.edgeSoftness,i.edgeGlow,0,+!!i.glassEnabled,i.glassOpacity,i.contourDeform,i.bandDensity,i.chromaticShift,i.metalScale,i.metalStretch,i.metalAngle,i.metalOffset,i.metalPhase,i.metalEvolution,i.metalRoughness,i.metalDepth,i.particleDensity,i.ribbonCount,i.ribbonWidth,i.ribbonTwist,i.ribbonFold,i.ribbonBreath,i.particleSize,i.particleBloom],3),[i.colorA,i.colorB,i.colorC,i.colorD,i.highlightColor,i.shellInner,i.shellMid,i.shellEdge,i.sheenColor,i.specColor,i.canvasColor,i.glowColor,...Iv].forEach((t,n)=>e.set(Lv(t),40+n*4))}function zv(e){let t=new Float32Array(136);return Rv(t,1,1,0,e),Array.from(t)}var Bv=221184,Vv=[`idle`,`thinking`],Hv=[`speed`,`contourDeform`,`bandDensity`,`chromaticShift`,`metalStretch`,`metalEvolution`,`metalRoughness`,`metalDepth`,`ribbonWidth`,`ribbonTwist`,`ribbonFold`,`ribbonBreath`,`zoom`,`warp`,`ridgeAmt`,`sharp`,`shade`,`exposure`,`edgeGlow`],Uv=[`colorA`,`colorB`,`colorC`,`colorD`,`highlightColor`,`glowColor`],Wv=[...Hv,...Uv],Gv=`thinking`,Kv=.22,qv=.65,Jv={siri:{numeric:{speed:{scale:.3},contourDeform:{scale:.3},zoom:{scale:.94},warp:{scale:.52},ridgeAmt:{scale:.48},sharp:{scale:.9},exposure:{scale:.68}},colors:{colorA:`#B5A674`,colorB:`#5E8794`,colorC:`#9A648A`,colorD:`#635B8A`,highlightColor:`#B6C4D2`,glowColor:`#6C688F`}},voiceWave:{numeric:{speed:{scale:.28},contourDeform:{scale:.3},zoom:{scale:.92},warp:{scale:.46},ridgeAmt:{scale:.42},exposure:{scale:.62}},colors:{colorA:`#08050B`,colorB:`#6A2F69`,colorC:`#8C4652`,colorD:`#55467F`,highlightColor:`#B58AA5`,glowColor:`#6C3E72`}},blueDrop:{numeric:{speed:{scale:.3},contourDeform:{scale:.35},zoom:{scale:.93},warp:{scale:.5},ridgeAmt:{scale:.46},sharp:{scale:.82},exposure:{scale:.66}},colors:{colorA:`#020812`,colorB:`#0A2C5A`,colorC:`#24678A`,colorD:`#A4C3CA`,highlightColor:`#9FC8D5`,glowColor:`#1F5076`}},violetEmber:{numeric:{speed:{scale:.28},contourDeform:{scale:.3},zoom:{scale:.92},warp:{scale:.46},ridgeAmt:{scale:.42},sharp:{scale:.78},exposure:{scale:.64}},colors:{colorA:`#0B0310`,colorB:`#2B1748`,colorC:`#593078`,colorD:`#9B78A8`,highlightColor:`#BCA6C2`,glowColor:`#593273`}},refractiveBlob:{numeric:{speed:{scale:.3},contourDeform:{scale:.32},zoom:{scale:.94},warp:{scale:.5},ridgeAmt:{scale:.44},sharp:{scale:.82},exposure:{scale:.68}},colors:{colorA:`#0F0B16`,colorB:`#403552`,colorC:`#776990`,colorD:`#AEA4BD`,highlightColor:`#C9C4D1`,glowColor:`#6E6185`}},particleRibbon:{numeric:{speed:{scale:.28},ribbonWidth:{scale:.62},ribbonTwist:{scale:.42},ribbonFold:{scale:.35},ribbonBreath:{scale:.18},exposure:{scale:.68}},colors:{colorA:`#3A6068`,colorB:`#375D78`,colorC:`#594E83`,colorD:`#854C7A`,highlightColor:`#B9CCD1`,glowColor:`#514C78`}},chromaticMetal:{numeric:{speed:{scale:.3},bandDensity:{scale:.62},chromaticShift:{scale:.35},metalStretch:{scale:.48},metalEvolution:{scale:.32},metalRoughness:{scale:1.35},metalDepth:{scale:.55},exposure:{scale:.72}},colors:{colorA:`#B8BCBA`,colorB:`#666B69`,colorC:`#9EA3A1`,colorD:`#282B2D`,highlightColor:`#D1D5D3`,glowColor:`#78898F`}},aurora:{numeric:{speed:{scale:.22},contourDeform:{scale:.3},zoom:{scale:.92},warp:{scale:.42},ridgeAmt:{scale:.38},sharp:{scale:.85},exposure:{scale:.62}},colors:{colorA:`#02050C`,colorB:`#1D6659`,colorC:`#285D78`,colorD:`#533E75`,highlightColor:`#92B6B3`,glowColor:`#286A62`}},frost:{numeric:{speed:{scale:.26},contourDeform:{scale:.28},zoom:{scale:.94},warp:{scale:.5},ridgeAmt:{scale:.46},sharp:{scale:.78},exposure:{scale:.72}},colors:{colorA:`#C3CDD5`,colorB:`#9AABB8`,colorC:`#768D9E`,colorD:`#536985`,highlightColor:`#D6DEE5`,glowColor:`#697D91`}},chrome:{numeric:{speed:{scale:.28},contourDeform:{scale:.35},zoom:{scale:.92},warp:{scale:.48},sharp:{scale:.74},exposure:{scale:.72}},colors:{colorA:`#A7AAA9`,colorB:`#6E7273`,colorC:`#363A3D`,colorD:`#101213`,highlightColor:`#CBCFCE`,glowColor:`#747A7B`}},opal:{numeric:{speed:{scale:.3},contourDeform:{scale:.32},zoom:{scale:.94},warp:{scale:.52},ridgeAmt:{scale:.48},exposure:{scale:.68}},colors:{colorA:`#C9C3BC`,colorB:`#6E9E91`,colorC:`#A17496`,colorD:`#68608E`,highlightColor:`#E1DCD5`,glowColor:`#82799B`}},spectrum:{numeric:{speed:{scale:.27},contourDeform:{scale:.3},zoom:{scale:.92},warp:{scale:.44},ridgeAmt:{scale:.38},exposure:{scale:.62}},colors:{colorA:`#B4BBC2`,colorB:`#285D8F`,colorC:`#91506F`,colorD:`#3F8873`,highlightColor:`#D8DDE1`,glowColor:`#386789`}},plasma:{numeric:{speed:{scale:.26},contourDeform:{scale:.28},zoom:{scale:.9},warp:{scale:.42},ridgeAmt:{scale:.36},sharp:{scale:.68},exposure:{scale:.6}},colors:{colorA:`#04020A`,colorB:`#084772`,colorC:`#1C5790`,colorD:`#174B84`,highlightColor:`#A5BBD0`,glowColor:`#14577F`}}},Yv=new Set(Wv);function Xv(e){return Yv.has(e)}function Zv(e){let t=Object.fromEntries(Wv.map(t=>[t,e[t]])),n={...e};for(let e of Wv)delete n[e];return{shared:n,profile:t}}function Qv(e){let t={...e},n=Jv[e.style];for(let[r,i]of Object.entries(n.numeric))t[r]=e[r]*i.scale+(i.offset??0);for(let e of Uv)t[e]=n.colors[e];return t}function $v(e,t=qv,n=Kv){if(!Number.isFinite(t)||t<0)throw RangeError(`Invalid orb transition duration: ${t}`);if(!Number.isFinite(n)||n<0)throw RangeError(`Invalid orb activation duration: ${n}`);let r=Zv(e),i=Zv(Qv(e));return{activationDuration:n,shared:r.shared,profiles:{idle:i.profile,thinking:r.profile},transitionDuration:t}}function ey(e){return $v({style:e,...Mv[e]})}function ty(e,t){return{...e.shared,...e.profiles[t]}}function ny(e,t,n,r){return Xv(n)?{...e,profiles:{...e.profiles,[t]:{...e.profiles[t],[n]:r}}}:{...e,shared:{...e.shared,[n]:r}}}function ry(e){if(!/^#[0-9a-f]{6}$/i.test(e))throw Error(`Invalid orb color: ${e}`);return[Number.parseInt(e.slice(1,3),16)/255,Number.parseInt(e.slice(3,5),16)/255,Number.parseInt(e.slice(5,7),16)/255]}function iy(e){return e<=.04045?e/12.92:((e+.055)/1.055)**2.4}function ay(e){return e<=.0031308?e*12.92:1.055*e**(1/2.4)-.055}function oy(e,t,n){if(n===0)return e;if(n===1)return t;let r=ry(e),i=ry(t);return`#${r.map((e,t)=>{let r=iy(e)+(iy(i[t])-iy(e))*n;return Math.min(255,Math.max(0,Math.round(ay(r)*255)))}).map(e=>e.toString(16).padStart(2,`0`)).join(``)}`.toUpperCase()}function sy(e){let t=Math.min(1,Math.max(0,e));return t*t*(3-2*t)}function cy(e){return 1-(1-Math.min(1,Math.max(0,e)))**3}function ly(e,t,n){let r=Math.min(1,Math.max(0,n));if(r===0)return{...e};if(r===1)return{...t};let i={...t};for(let n of Hv)i[n]=e[n]+(t[n]-e[n])*r;for(let n of Uv)i[n]=oy(e[n],t[n],r);return i}function uy(e){let t=e.state,n={...e.params},r={...e.params},i=e.state,a=0,o=0;function s(e){if(o===0)return{...r};let t=Math.max(0,e-a)/o,s=i===`thinking`?cy(t):sy(t);return ly(n,r,s)}return{sample(e,c){return e.state===t?r={...e.params}:(n=s(c),r={...e.params},i=e.state,a=c,o=Math.max(0,(e.state===`thinking`?e.activationDuration:e.transitionDuration)*1e3),t=e.state),s(c)}}}var dy=`// Glass Liquid — curated flow programs with an optional glass shell.
//
// The local presets use independent spatial models for Siri-like sheets,
// symmetric colour waves, aurora curtains, frost flow, neural interference,
// liquid chrome, opal interference, a voice membrane, a blue liquid drop, and
// a violet molten core, plus a chromatic brushed-metal field. The legacy liquid
// bank remains below for compatibility with older shared shader
// code, but is not exposed as an editor preset.
//
// When enabled, the shell uses a signed-distance refraction profile around the
// boundary, asymmetric spectral separation, and two directional edge lights.
// The fluid is resampled through that profile, so glass changes the image rather
// than covering it with a translucent white face.
//
// ---------------------------------------------------------------------------
// Analytic optical diffusion without a convolution.
// ---------------------------------------------------------------------------
//
// The source used a thirteen-tap 5px frost blur. This port keeps one fluid
// evaluation and applies the equivalent gaussian in the frequency domain:
//
//  1. **Per-octave attenuation, inside \`lqFbm\`.** Convolving with a gaussian of
//     sigma σ scales a component at wavenumber k by exp(-k²σ²/2). An fbm's
//     octaves have known wavenumbers — octave i sits at 2.03^i times the base —
//     so each octave's amplitude is scaled by its own factor and the field is
//     sampled once. The mean is untouched (a blur preserves it), so only the
//     deviation from 0.5 is scaled and the \`s / m\` normaliser is unchanged.
//     Every caller passes the diffusion sigma in its own input units, so detail
//     attenuation continues to track \`zoom\`.
//
//  2. **Value-space quadrature at every pointwise nonlinearity.** This is the
//     part that is easy to get wrong. \`blur(ridge(f))\` is not \`ridge(blur(f))\`:
//     attenuating first and ridging after leaves filaments thin and hard where
//     the blur should have spread them, which is exactly how the earlier
//     analytic-edge version failed. So \`lqFbm\` also returns the standard
//     deviation of the detail the attenuation removed — within a gaussian
//     window an octave scaled by β contributes variance ∝ (1 - β²), NOT
//     (1 - β)² — and every nonlinearity applied to that field integrates it
//     back out with a three-point Gauss-Hermite rule (exact through the fourth
//     moment). Three evaluations of a function of one float, not three
//     evaluations of the noise. \`lqRidgeS\`/\`lqStepS\`/\`lqPowS\` below; Nectar's
//     branch has the fbm inside a \`sin\`, where the same integral is closed-form
//     (E[sin(A + cε)] = sin A · exp(-c²σ²/2)), so it damps the sine instead.
//
//  3. **One continuous disc edge.** The fluid always reaches the sphere
//     boundary. Glass changes its sample coordinates near that boundary, so
//     toggling the shell cannot reveal a second hard-clipped silhouette.
//
// Deliberately NOT ported, and why:
//   - The liquid grain. It sits below display-pixel scale and adds noise rather
//     than useful optical detail, so Glass Liquid has no Grain parameter.
//   - The two contact-shadow ellipses under the ball and its outer
//     \`0 26px 50px -24px\` drop shadow. The Orbs family cut the source app's
//     floor at the user's request, and the export paints over \`Color.black\`.
//
// Scalar controls are packed after \`time\`; the colour bank starts on the next
// 16-byte boundary. The TypeScript writer mirrors this order exactly.
struct Uniforms {
  size:           vec2<f32>,
  time:           f32,
  speed:          f32,
  radius:         f32,
  zoom:           f32,
  warp:           f32,
  ridgeAmt:       f32,
  sharp:          f32,
  shade:          f32,
  sheen:          f32,
  gloss:          f32,
  shellMidAlpha:  f32,
  shellEdgeAlpha: f32,
  exposure:       f32,
  style:          f32,
  edgeSoftness:   f32,
  edgeGlow:       f32,
  paletteCount:   f32,
  glassEnabled:   f32,
  glassOpacity:   f32,
  contourDeform:  f32,
  bandDensity:    f32,
  chromaticShift: f32,
  metalScale:     f32,
  metalStretch:   f32,
  metalAngle:     f32,
  metalOffset:    f32,
  metalPhase:     f32,
  metalEvolution: f32,
  metalRoughness: f32,
  metalDepth:     f32,
  particleDensity: f32,
  ribbonCount:     f32,
  ribbonWidth:     f32,
  ribbonTwist:     f32,
  ribbonFold:      f32,
  ribbonBreath:    f32,
  particleSize:    f32,
  particleBloom:   f32,
  colorA:         vec4<f32>,
  colorB:         vec4<f32>,
  colorC:         vec4<f32>,
  colorD:         vec4<f32>,
  highlightColor: vec4<f32>,
  shellInner:     vec4<f32>,
  shellMid:       vec4<f32>,
  shellEdge:      vec4<f32>,
  sheenColor:     vec4<f32>,
  specColor:      vec4<f32>,
  canvasColor:    vec4<f32>,
  glowColor:      vec4<f32>,
  paletteStop0:    vec4<f32>,
  paletteStop1:    vec4<f32>,
  paletteStop2:    vec4<f32>,
  paletteStop3:    vec4<f32>,
  paletteStop4:    vec4<f32>,
  paletteStop5:    vec4<f32>,
  paletteStop6:    vec4<f32>,
  paletteStop7:    vec4<f32>,
  paletteStop8:    vec4<f32>,
  paletteStop9:    vec4<f32>,
  paletteStop10:   vec4<f32>,
  paletteStop11:   vec4<f32>,
};
@group(0) @binding(0) var<uniform> u: Uniforms;

// ── The Orbs edge bank (WGSL) ───────────────────────────────────────────────
// Two knobs every orb on the shelf carries: how soft its limb is, and how far
// it glows past it. See effects/_shared/edge.ts for the contract.
//
// THREE files must agree — edge.wgsl, edge.metal, edge.sksl. Change one, change
// all three, or the Code tab starts lying about what it ships.

// How much wider than the shipped feather the Edge softness slider is asking
// for. 0.005 is the width every orb was authored with, so this returns exactly
// 0 at the default and every edge expression collapses to the constant it
// replaced — the defaults are bit-identical to the render before the bank.
fn mfEdgeD(soft: f32) -> f32 {
  return soft - 0.005;
}

// The halo an orb throws past its own limb.
//
// ADDED, never subtracted: whatever the orb already paints out there — a
// studio wall, its own exp() bleed, the sheet's cones — survives untouched.
// That is what lets this be adopted by seventeen shaders whose backdrops have
// nothing in common.
//
// \`glow == 0\` returns \`col\` by an early exit rather than by adding zero. Both
// are exact, but the exit also skips the length() on the ~60% of the frame
// outside the ball, and 0 is the default.
fn mfEdgeGlow(col: vec3<f32>, uv: vec2<f32>, ctr: vec2<f32>, rad: f32,
              soft: f32, glow: f32, glowRGB: vec3<f32>) -> vec3<f32> {
  if (glow <= 0.0) { return col; }
  let r = length(uv - ctr);
  // Fenced to the outside of the limb by the same softness the limb uses, so
  // the halo starts where the ball stops however soft that boundary is. Without
  // it the exp() is 1 across the whole disc and washes the face flat.
  let outside = smoothstep(rad - max(soft, 0.0005), rad + max(soft, 0.0005), r);
  return col + glowRGB * (glow * exp(-max(r - rad, 0.0) * 11.0) * outside);
}


// ── The Orbs palette-ramp bank (WGSL) ───────────────────────────────────────
// The add/remove colour list, evaluated INSIDE the shader so every stop paints
// its own region of the ball instead of being averaged into a role colour.
// See effects/_shared/ramp.ts for the contract.
//
// THREE files must agree — ramp.wgsl, ramp.metal, ramp.sksl. Change one, change
// all three, or the Code tab starts lying about what it ships.

// One stop, picked without a dynamic array index.
//
// A \`var\` array indexed by a runtime value is the shape that spills to scratch
// memory on the GPUs this project cares about (PERFORMANCE.md); twelve selects
// stay in registers and are branchless on every backend. Written once here so
// no adopting shader has to.
fn mfRampPick(idx: f32,
              s0: vec3<f32>, s1: vec3<f32>, s2:  vec3<f32>, s3:  vec3<f32>,
              s4: vec3<f32>, s5: vec3<f32>, s6:  vec3<f32>, s7:  vec3<f32>,
              s8: vec3<f32>, s9: vec3<f32>, s10: vec3<f32>, s11: vec3<f32>) -> vec3<f32> {
  var r = s0;
  r = select(r, s1,  idx == 1.0);
  r = select(r, s2,  idx == 2.0);
  r = select(r, s3,  idx == 3.0);
  r = select(r, s4,  idx == 4.0);
  r = select(r, s5,  idx == 5.0);
  r = select(r, s6,  idx == 6.0);
  r = select(r, s7,  idx == 7.0);
  r = select(r, s8,  idx == 8.0);
  r = select(r, s9,  idx == 9.0);
  r = select(r, s10, idx == 10.0);
  r = select(r, s11, idx == 11.0);
  return r;
}

// The CYCLIC ramp: \`t\` wraps, and the last stop runs back into the first.
//
// This is the one a generated-colour orb wants. Prism's hue comes from a cosine
// of an unbounded scalar field, so its colour has always been periodic — a
// clamped ramp would flatten every band past t == 1 into one colour and throw
// the banding away. Wrapping keeps the field's structure exactly and only swaps
// what the structure is *coloured* with.
//
// NOT ONE BRANCH IN HERE, and that is load-bearing rather than tidy. An orb
// evaluates this next to a \`fract(sin(x) * 43758.5453)\` grain hash, which
// amplifies a last-bit change in its argument by ~44000x. Any \`if\` in this file
// or at a call site splits the fragment's basic block, the compiler stops
// folding \`uv / rad\` into its uses, and the hash turns that into speckle up to
// 33/255 — measured, on exactly the first cut of this bank. Straight-line code
// keeps the untouched render bit-identical. Same reasoning as the early-out
// guards every orb carries; see the note in orb-prism.wgsl.
fn mfRampCyc(tIn: f32, n: f32,
             s0: vec3<f32>, s1: vec3<f32>, s2:  vec3<f32>, s3:  vec3<f32>,
             s4: vec3<f32>, s5: vec3<f32>, s6:  vec3<f32>, s7:  vec3<f32>,
             s8: vec3<f32>, s9: vec3<f32>, s10: vec3<f32>, s11: vec3<f32>) -> vec3<f32> {
  let k  = clamp(floor(n + 0.5), 1.0, 12.0);
  let x  = fract(tIn) * k;
  let i0 = min(floor(x), k - 1.0);
  let i1 = select(i0 + 1.0, 0.0, i0 + 1.0 >= k);   // the wrap
  return mix(mfRampPick(i0, s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11),
             mfRampPick(i1, s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11),
             x - i0);
}

// The CLAMPED ramp: stop 0 at t == 0, the last stop at t == 1, held outside.
//
// This is the one an orb with an authored dark→light body ramp wants — the
// four-stop Deep/Mid/Surge/Crest shape, where the ends really are ends.
//
// Branchless for the same reason as \`mfRampCyc\`. The single-stop case falls out
// of the arithmetic rather than needing an early return: k == 1 makes the span
// zero, so x is 0, i0 is 0 and the mix weight is 0 — s0, exactly.
fn mfRampLin(tIn: f32, n: f32,
             s0: vec3<f32>, s1: vec3<f32>, s2:  vec3<f32>, s3:  vec3<f32>,
             s4: vec3<f32>, s5: vec3<f32>, s6:  vec3<f32>, s7:  vec3<f32>,
             s8: vec3<f32>, s9: vec3<f32>, s10: vec3<f32>, s11: vec3<f32>) -> vec3<f32> {
  let k  = clamp(floor(n + 0.5), 1.0, 12.0);
  let x  = clamp(tIn, 0.0, 1.0) * (k - 1.0);
  let i0 = clamp(floor(x), 0.0, max(k - 2.0, 0.0));
  return mix(mfRampPick(i0,     s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11),
             mfRampPick(i0 + 1.0, s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11),
             x - i0);
}

// ── The ramp as ONE value ───────────────────────────────────────────────────
//
// Thirteen uniforms is a reasonable thing for a shader to hold and a terrible
// thing for a helper to take. Several orbs make their body colour deep inside
// one — Glass·Liquid's fluid, the studio orbs' environment mirrors — and in the
// MSL these files are transcribed against, a helper cannot read the stitchable
// entry point's arguments, so the palette has to be handed down. Bundled like
// this that is one parameter instead of thirteen, and the three languages stay
// line-for-line.
//
// The stops come back out by CONSTANT index only, so this is still not a
// dynamically indexed array and still cannot spill to scratch memory.
struct MfRamp {
  n:   f32,
  s0:  vec3<f32>, s1:  vec3<f32>, s2:  vec3<f32>, s3:  vec3<f32>,
  s4:  vec3<f32>, s5:  vec3<f32>, s6:  vec3<f32>, s7:  vec3<f32>,
  s8:  vec3<f32>, s9:  vec3<f32>, s10: vec3<f32>, s11: vec3<f32>,
};

fn mfRampOf(n: f32,
            s0: vec3<f32>, s1: vec3<f32>, s2:  vec3<f32>, s3:  vec3<f32>,
            s4: vec3<f32>, s5: vec3<f32>, s6:  vec3<f32>, s7:  vec3<f32>,
            s8: vec3<f32>, s9: vec3<f32>, s10: vec3<f32>, s11: vec3<f32>) -> MfRamp {
  return MfRamp(n, s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11);
}

fn mfRampCycR(t: f32, r: MfRamp) -> vec3<f32> {
  return mfRampCyc(t, r.n, r.s0, r.s1, r.s2, r.s3, r.s4, r.s5,
                   r.s6, r.s7, r.s8, r.s9, r.s10, r.s11);
}

fn mfRampLinR(t: f32, r: MfRamp) -> vec3<f32> {
  return mfRampLin(t, r.n, r.s0, r.s1, r.s2, r.s3, r.s4, r.s5,
                   r.s6, r.s7, r.s8, r.s9, r.s10, r.s11);
}


// Fluid geometry, in ball radii (|p| == 1 on the ball's edge, y up).
const GL_FU:   f32 = 0.88172043;   // canvas half-side = 0.82/0.93 R

// Pure fluid keeps tighter diffusion; enabling glass restores the source's 5px
// frosted diffusion inside the inset shell.
const GL_BSIG_CLEAR: f32 = 0.01800000;
const GL_BSIG_GLASS: f32 = 0.03990000;

// --- the three constants the frequency-domain blur is fitted on -------------
// A gaussian's response is exp(-k²σ²/2), so GL_KA is k²/2 for the wavenumber
// where smoothstep-interpolated value noise actually keeps its energy. The
// textbook choice — one cycle per noise cell, k = 2π, GL_KA = 19.74 — blurs too
// hard, because the smoothstep interpolation is itself a low-pass and pulls the
// effective k down to about 3.5. Fitted against the 13-tap render.
const GL_KA:  f32 = 6.0;
// (2.03)² — how σ grows, in its own octave's cells, from one octave to the next.
const GL_KG:  f32 = 4.1209;
// The warp field displaces the fluid rather than colouring it, so blurring the
// image does not attenuate it as strongly as the model says. Also fitted.
const GL_KWA: f32 = 0.5;
// One value-noise octave's standard deviation about its own mean, as a fraction
// of its range — the scale that turns "amplitude the attenuation removed" into
// "how far the removed detail typically pushed the value".
const GL_KR:  f32 = 0.32;
const GL_GH:  f32 = 1.73205081;   // sqrt(3), the 3-point Gauss-Hermite abscissa

// Pure fluid reaches the ball edge.
const GL_CLEAR_EA: f32 = 0.995;
const GL_CLEAR_EB: f32 = 1.04;

// ---------------------------------------------------------------------------
// The sheet's liquid noise bank. Five octaves, gain .5, normalised by the
// weight sum, and rotated every octave. This is NOT the bank the sheet's Prism
// screen uses (a different hash, gain .55, unnormalised, no rotation).
// ---------------------------------------------------------------------------
fn lqHash(pIn: vec2<f32>) -> f32 {
  var p = fract(pIn * vec2<f32>(123.34, 456.21));
  p = p + vec2<f32>(dot(p, p + vec2<f32>(45.32)));
  return fract(p.x * p.y);
}

fn lqNoise(p: vec2<f32>) -> f32 {
  let i = floor(p);
  var f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(mix(lqHash(i), lqHash(i + vec2<f32>(1.0, 0.0)), f.x),
             mix(lqHash(i + vec2<f32>(0.0, 1.0)), lqHash(i + vec2<f32>(1.0, 1.0)), f.x), f.y);
}

// The fbm, pre-blurred. \`bs\` is the blur's sigma expressed in THIS call's input
// units — the caller scales it by whatever it scaled the domain by. Returns
// \`.x\` the attenuated value and \`.y\` the standard deviation of the detail the
// attenuation took out, which is what a following nonlinearity has to integrate
// over. Both are exact for a gaussian window: the surviving amplitude is β and
// the variance that leaves is (1 - β²), per octave, weighted by that octave's
// own share of the normalised sum.
fn lqFbm(pIn: vec2<f32>, bs: f32) -> vec2<f32> {
  var p = pIn;
  var s:  f32 = 0.0;
  var a:  f32 = 0.5;
  var m:  f32 = 0.0;
  var vr: f32 = 0.0;
  let e = -GL_KA * bs * bs;
  var g: f32 = 1.0;
  for (var i: i32 = 0; i < 5; i = i + 1) {
    let b = exp(e * g);
    s  = s  + a * (0.5 + b * (lqNoise(p) - 0.5));
    vr = vr + a * a * (1.0 - b * b);
    m  = m + a;
    a  = a * 0.5;
    g  = g * GL_KG;
    // GLSL's mat2(.8,.6,-.6,.8) is COLUMN-major — columns (.8,.6) and
    // (-.6,.8) — so the product is written out rather than constructed.
    p = vec2<f32>(0.8 * p.x - 0.6 * p.y, 0.6 * p.x + 0.8 * p.y) * 2.03;
  }
  return vec2<f32>(s / m, GL_KR * sqrt(vr) / m);
}

fn lqRidge(v: f32, k: f32) -> f32 {
  return pow(clamp(1.0 - abs(v * 2.0 - 1.0), 0.0, 1.0), k);
}

// The sheet's four-stop ramp, shared by every branch of every program.
fn lqRamp(v: f32, cA: vec3<f32>, cB: vec3<f32>, cC: vec3<f32>, cD: vec3<f32>) -> vec3<f32> {
  var c = mix(cA, cB, smoothstep(0.0, 0.45, v));
  c = mix(c, cC, smoothstep(0.38, 0.72, v));
  c = mix(c, cD, smoothstep(0.68, 1.0, v));
  // The editor's four colours are the default ramp. An optional custom palette
  // can replace them without changing the scalar field that produces \`v\`.
  return select(c, mfRampLin(v, u.paletteCount,
                             u.paletteStop0.rgb, u.paletteStop1.rgb, u.paletteStop2.rgb,
                             u.paletteStop3.rgb, u.paletteStop4.rgb, u.paletteStop5.rgb,
                             u.paletteStop6.rgb, u.paletteStop7.rgb, u.paletteStop8.rgb,
                             u.paletteStop9.rgb, u.paletteStop10.rgb, u.paletteStop11.rgb), u.paletteCount > 0.5);
}

// ---------------------------------------------------------------------------
// The three nonlinearities the fluid applies to a pre-blurred field, each
// integrated over the detail \`lqFbm\` attenuated away. Three-point
// Gauss-Hermite — nodes 0 and ±sqrt(3)·sd, weights 4/6 and 1/6 — reproduces a
// gaussian's second AND fourth moments, which is what keeps a ridged filament
// spreading as it dims instead of just dimming. \`vs\` is an \`lqFbm\` result:
// \`.x\` the value, \`.y\` that standard deviation.
// ---------------------------------------------------------------------------
fn lqRidgeS(vs: vec2<f32>, k: f32) -> f32 {
  let d = GL_GH * vs.y;
  return (lqRidge(vs.x - d, k) + 4.0 * lqRidge(vs.x, k) + lqRidge(vs.x + d, k)) / 6.0;
}

fn lqStepS(vs: vec2<f32>, a: f32, b: f32) -> f32 {
  let d = GL_GH * vs.y;
  return (smoothstep(a, b, vs.x - d) + 4.0 * smoothstep(a, b, vs.x)
        + smoothstep(a, b, vs.x + d)) / 6.0;
}

fn lqPowS(vs: vec2<f32>, k: f32) -> f32 {
  let d = GL_GH * vs.y;
  return (pow(clamp(vs.x - d, 0.0, 1.0), k) + 4.0 * pow(clamp(vs.x, 0.0, 1.0), k)
        + pow(clamp(vs.x + d, 0.0, 1.0), k)) / 6.0;
}

// ---------------------------------------------------------------------------
// Curated local flow programs. Each preset owns a different spatial model;
// colour changes are secondary to silhouette, frequency, and motion structure.
// ---------------------------------------------------------------------------

fn glsFinishPresetFluid(colorIn: vec3<f32>, p: vec2<f32>) -> vec3<f32> {
  var color = colorIn;
  color = mix(color, u.highlightColor.rgb,
              u.shade * 0.22 * smoothstep(0.15, 1.15, dot(p, vec2<f32>(-0.32, 0.78))));
  color = color * (1.0 - u.shade * 0.34
                  * smoothstep(-0.1, 1.2, dot(p, vec2<f32>(0.45, -0.62))));
  color = color * (1.0 - u.shade * 0.22 * smoothstep(0.72, 1.08, length(p)));
  return clamp(color, vec3<f32>(0.0), vec3<f32>(1.0));
}

fn glsFinishEmissionFluid(colorIn: vec3<f32>, p: vec2<f32>) -> vec3<f32> {
  var color = colorIn;
  if (u.glassEnabled > 0.5) {
    color = mix(color, u.highlightColor.rgb,
                u.shade * 0.22 * smoothstep(0.15, 1.15, dot(p, vec2<f32>(-0.32, 0.78))));
  }
  color = color * (1.0 - u.shade * 0.34
                  * smoothstep(-0.1, 1.2, dot(p, vec2<f32>(0.45, -0.62))));
  color = color * (1.0 - u.shade * 0.22 * smoothstep(0.72, 1.08, length(p)));
  return clamp(color, vec3<f32>(0.0), vec3<f32>(1.0));
}

fn glsSiriBand(q: vec2<f32>, drift: f32, phaseOffset: f32, amplitude: f32,
               mainY: f32, envelope: f32, softness: f32) -> vec2<f32> {
  let y = amplitude * envelope * sin(q.x * 1.0 + drift + phaseOffset);
  let distanceToLine = abs(q.y - y);
  let line = 0.018 / (sqrt(distanceToLine * distanceToLine + softness * softness) + 0.026);
  let bandDistance = max(0.0, max(q.y - max(mainY, y), min(mainY, y) - q.y));
  let band = 0.018 / (bandDistance + 0.075);
  return vec2<f32>(line, band);
}

fn glsSiriFluid(p: vec2<f32>, t: f32) -> vec3<f32> {
  // The reference wave is a main sinusoid plus four chromatically separated
  // waves. Their enclosed bands carry colour while the shared crest stays hot.
  let scale = 0.74 + u.zoom * 0.34;
  let q = p / scale;
  let xNorm = q.x;
  let envelopeBase = cos(1.57079633 * min(abs(0.9 * xNorm), 1.0));
  let envelope = envelopeBase * envelopeBase;
  let low = 0.5 + 0.5 * cos(t * 0.37);
  let mid = 0.5 + 0.5 * sin(t * 0.51 + 1.2);
  let high = 0.5 + 0.5 * cos(t * 0.73 + 2.1);
  let drift = t * 2.4;
  let mainAmplitude = 0.25 + u.ridgeAmt * 0.075 + low * 0.018;
  let bandAmplitude = mainAmplitude + mid * 0.025 + high * 0.018;
  let mainY = mainAmplitude * envelope * sin(q.x * 1.1 + drift);
  let separation = 1.85 + u.warp * 0.2 + mid * 0.28;
  let softness = 0.035 + (1.0 - u.ridgeAmt) * 0.018 + mid * 0.006;

  let band0 = glsSiriBand(q, drift, -separation, bandAmplitude, mainY, envelope, softness);
  let band1 = glsSiriBand(q, drift, -separation * 0.34, bandAmplitude, mainY, envelope, softness);
  let band2 = glsSiriBand(q, drift, separation * 0.34, bandAmplitude, mainY, envelope, softness);
  let band3 = glsSiriBand(q, drift, separation, bandAmplitude, mainY, envelope, softness);
  let w0 = band0.x + band0.y;
  let w1 = band1.x + band1.y;
  let w2 = band2.x + band2.y;
  let w3 = band3.x + band3.y;
  let total = w0 + w1 + w2 + w3;
  let dominant0 = w0 * w0;
  let dominant1 = w1 * w1;
  let dominant2 = w2 * w2;
  let dominant3 = w3 * w3;
  let dominantTotal = dominant0 + dominant1 + dominant2 + dominant3;
  let spectral = (u.colorA.rgb * dominant0 + u.colorC.rgb * dominant1
                + u.colorB.rgb * dominant2 + u.colorD.rgb * dominant3)
                / max(dominantTotal, 0.0001);
  let energy = (1.0 - exp(-total * 0.58)) * envelope;
  let mainDistance = abs(q.y - mainY);
  let whiteCore = exp(-mainDistance * mainDistance / 0.0028) * envelope;
  let glassFill = select(0.0, 1.0, u.glassEnabled > 0.5);
  let atmosphere = mix(u.colorD.rgb, u.colorB.rgb,
                       smoothstep(-0.7, 0.7, q.y)) * 0.018 * glassFill;
  var color = atmosphere + spectral * energy * 1.14;
  color = color + u.highlightColor.rgb * whiteCore * (0.18 + 0.1 * low);
  let emissionMask = mix(smoothstep(0.08, 0.25, energy + whiteCore * 0.12),
                         1.0, glassFill);
  color = color * emissionMask;
  color = color / (vec3<f32>(1.0) + color * 0.18);
  return glsFinishEmissionFluid(color, p);
}

fn glsSpectrumHeight(q: vec2<f32>, t: f32, frequency: f32,
                     phaseOffset: f32, amplitude: f32) -> f32 {
  let x = q.x * 2.15;
  let envelope = pow(4.0 / (4.0 + x * x), 4.0);
  let breathing = 0.82 + 0.18 * sin(t * 0.48 + phaseOffset * 0.7);
  let wave = abs(sin(frequency * x - t * 1.36 + phaseOffset));
  return envelope * amplitude * breathing * (0.28 + 0.72 * wave);
}

fn glsSpectrumLayer(q: vec2<f32>, height: f32, softness: f32) -> f32 {
  return (1.0 - smoothstep(max(height - softness, 0.0), height + softness, abs(q.y)))
         * smoothstep(0.0, 0.045, height);
}

fn glsSpectrumFluid(p: vec2<f32>, t: f32) -> vec3<f32> {
  // Three symmetric filled wave surfaces orbit a persistent support line. This
  // keeps the iOS 9 voice-field silhouette without depending on canvas strokes.
  let scale = 0.74 + u.zoom * 0.34;
  let q = p / scale;
  let amplitude = 0.26 + u.ridgeAmt * 0.27;
  let frequency = 0.72 + u.warp * 0.095;
  let softness = 0.026 + (1.0 - u.ridgeAmt) * 0.032;
  let h0 = glsSpectrumHeight(q, t, frequency * 0.82, -1.2, amplitude * 0.72);
  let h1 = glsSpectrumHeight(q, t, frequency, 0.45, amplitude);
  let h2 = glsSpectrumHeight(q, t, frequency * 1.17, 2.05, amplitude * 0.82);
  let l0 = glsSpectrumLayer(q, h0, softness);
  let l1 = glsSpectrumLayer(q, h1, softness);
  let l2 = glsSpectrumLayer(q, h2, softness);
  let spectrumX = q.x * 2.15;
  let envelope = pow(4.0 / (4.0 + spectrumX * spectrumX), 4.0);
  let support = exp(-q.y * q.y / 0.00072) * envelope;
  let total = l0 + l1 + l2;
  let spectral = (u.colorB.rgb * l0 + u.colorC.rgb * l1 + u.colorD.rgb * l2)
                 / max(total, 0.001);
  let glassFill = select(0.0, 1.0, u.glassEnabled > 0.5);
  var color = u.colorD.rgb * 0.025 * glassFill
            + spectral * (1.0 - exp(-total * 0.86));
  color = color + u.colorA.rgb * support * 0.58;
  color = color / (vec3<f32>(1.0) + color * 0.2);
  return glsFinishEmissionFluid(color, p);
}

fn glsAuroraLayer(p: vec2<f32>, t: f32, offset: f32) -> f32 {
  let drift = t * 0.18 + offset * 2.5;
  let wave1 = sin(p.x * (2.0 + u.warp * 0.13) + drift + offset * 6.0) * 0.25;
  let wave2 = sin(p.x * 3.7 + drift * 1.3 + offset * 4.0) * 0.12;
  let wave3 = sin(p.x * 7.2 + drift * 0.7 + offset * 8.0) * 0.055;
  let noiseValue = lqFbm(vec2<f32>(p.x * 1.6 + drift * 0.35,
                                   p.y * 0.8 + offset * 3.0), 0.018).x;
  let center = offset * 0.46 + wave1 + wave2 + wave3
               + (noiseValue - 0.5) * 0.28;
  let dist = abs(p.y - center);
  let glow = exp(-dist * dist * (13.0 - 5.0 * u.ridgeAmt));
  let shimmer = lqFbm(vec2<f32>(p.x * 4.0 + t * 0.22,
                                p.y * 7.0 + offset * 5.0), 0.012).x;
  return glow * (0.64 + 0.36 * shimmer);
}

fn glsAuroraFluid(p: vec2<f32>, t: f32) -> vec3<f32> {
  let q = p * (0.82 + u.zoom * 0.58);
  let l0 = glsAuroraLayer(q, t, -0.72);
  let l1 = glsAuroraLayer(q, t, 0.0);
  let l2 = glsAuroraLayer(q, t, 0.72);
  var color = u.colorA.rgb * (0.46 + 0.18 * (q.y + 1.0));
  color = color + u.colorB.rgb * l0 * 1.3;
  color = color + u.colorC.rgb * l1 * 1.15;
  color = color + u.colorD.rgb * l2 * 1.2;
  color = color + mix(u.colorB.rgb, u.colorD.rgb, 0.5) * min(l0 * l2, l1) * 0.65;

  let starUv = (q + vec2<f32>(1.0)) * 18.0;
  let starCell = floor(starUv);
  let starHash = lqHash(starCell);
  let starPoint = exp(-dot(fract(starUv) - vec2<f32>(0.5),
                            fract(starUv) - vec2<f32>(0.5)) * 90.0);
  let stars = step(0.965, starHash) * starPoint
              * (0.55 + 0.45 * sin(t * (1.0 + starHash * 2.0) + starHash * 6.28));
  color = color + u.highlightColor.rgb * stars * (1.0 - clamp(l0 + l1 + l2, 0.0, 1.0));
  color = color / (vec3<f32>(1.0) + color * 0.28);
  return glsFinishPresetFluid(color, p);
}

fn glsRotate(p: vec2<f32>, angle: f32) -> vec2<f32> {
  let c = cos(angle);
  let s = sin(angle);
  return vec2<f32>(c * p.x - s * p.y, s * p.x + c * p.y);
}

fn glsNeuroShape(pIn: vec2<f32>, t: f32) -> f32 {
  var p = pIn * (0.34 + 0.08 * u.zoom);
  var sineAccum = vec2<f32>(0.0);
  var result = vec2<f32>(0.0);
  var scale = 8.0;
  for (var j: i32 = 0; j < 11; j = j + 1) {
    p = glsRotate(p, 1.0);
    sineAccum = glsRotate(sineAccum, 1.0);
    let layer = p * scale + vec2<f32>(f32(j)) + sineAccum - vec2<f32>(t * 0.34);
    sineAccum = sineAccum + sin(layer);
    result = result + (vec2<f32>(0.5) + 0.5 * cos(layer)) / scale;
    scale = scale * 1.16;
  }
  return result.x + result.y;
}

fn glsPlasmaFluid(p: vec2<f32>, t: f32) -> vec3<f32> {
  let shape = glsNeuroShape(p, t);
  let phase = shape * (10.0 + u.warp) + p.x * 1.7 - p.y * 1.3 - t * 0.52;
  let ridgeWidth = 0.62 - 0.24 * u.ridgeAmt;
  let primary = pow(abs(cos(phase)), max(1.3, u.sharp * ridgeWidth));
  let secondary = pow(abs(cos(phase * 0.53 + atan2(p.y, p.x) * 2.0 + t * 0.21)),
                      max(1.6, u.sharp * (ridgeWidth + 0.1)));
  let filaments = max(primary, secondary * 0.64);
  let core = pow(primary, 4.0);
  let polarity = 0.5 + 0.5 * sin(phase * 0.37 + shape * 3.0);
  var color = mix(u.colorA.rgb * 0.42, u.colorD.rgb * 0.48, polarity * 0.46);
  color = mix(color, u.colorB.rgb, filaments * 0.72);
  color = mix(color, u.colorC.rgb, core * 0.68);
  color = color + u.highlightColor.rgb * pow(core, 3.0) * 0.16;
  color = color / (vec3<f32>(1.0) + color * 0.34);
  return glsFinishPresetFluid(color, p);
}

fn glsChromeFluid(p: vec2<f32>, t: f32) -> vec3<f32> {
  var q = p * (1.0 + u.zoom * 0.35);
  let amplitude = 0.028 * u.warp;
  for (var i: i32 = 1; i <= 9; i = i + 1) {
    let fi = f32(i);
    q.x = q.x + amplitude / fi * cos(fi * 2.7 * q.y + t * 0.46);
    q.y = q.y + amplitude / fi * cos(fi * 3.1 * q.x - t * 0.4);
  }
  let denominator = max(abs(sin(t * 0.24 - q.y - q.x)), 0.045);
  let flare = clamp(1.0 / denominator, 0.0, 18.0);
  let metal = smoothstep(1.15, 7.5, flare);
  let fold = 0.5 + 0.5 * cos((q.x - q.y) * (3.2 + u.sharp * 0.28) + t * 0.32);
  let value = clamp(metal * 0.74 + fold * 0.36, 0.0, 1.0);
  var color = lqRamp(value, u.colorD.rgb, u.colorC.rgb, u.colorB.rgb, u.colorA.rgb);
  color = mix(color, u.colorA.rgb, pow(metal, 5.0) * 0.62);
  return glsFinishPresetFluid(color, p);
}

fn glsChromaticMetalPhase(p: vec2<f32>, t: f32) -> f32 {
  let angle = u.metalAngle * 0.01745329252;
  let scale = max(u.metalScale, 0.05);
  let stretch = mix(0.48, 1.58, clamp(u.metalStretch, 0.0, 1.0));
  var q = glsRotate(p / scale, angle);
  q = vec2<f32>(q.x / stretch, q.y * stretch);

  // The reference advances continuously while local reflections evolve out of
  // phase. Travelling domain waves provide that deformation without rotating
  // the entire pattern as one rigid layer. Integer harmonics keep a clean loop.
  let cycle = t * 0.46 + u.metalPhase * 6.28318530718;
  let evolution = clamp(u.metalEvolution, 0.0, 2.0);
  q.x = q.x + sin(q.y * 1.86 - cycle) * 0.095 * evolution;
  q.x = q.x + sin((q.x + q.y) * 1.28 + cycle * 2.0 + 1.4) * 0.045 * evolution;
  q.y = q.y + sin(q.x * 1.52 + cycle + 0.8) * 0.07 * evolution;

  let repeats = max(u.bandDensity, 1.0);
  return q.x * repeats * 2.18
       + sin(q.y * (1.3 + repeats * 0.26) - cycle) * 0.56 * evolution
       + sin((q.x - q.y) * 1.34 + cycle * 2.0 + 1.7) * 0.27 * evolution
       + sin((q.x * 0.72 + q.y) * 2.1 - cycle * 3.0 + 0.35) * 0.11 * evolution
       + sin(cycle) * 0.1
       + sin(cycle * 3.0 + 0.7) * 0.035
       + cycle
       + u.metalOffset * 6.28318530718;
}

fn glsChromaticMetalTone(phase: f32) -> f32 {
  let wave = 0.5 + 0.5 * cos(phase);
  let roughness = clamp(u.metalRoughness, 0.0, 1.0);
  let depth = clamp(u.metalDepth, 0.0, 1.0);
  let edge = 0.025 + roughness * 0.18;
  let broadReflection = smoothstep(0.5 - edge, 0.5 + edge, wave);
  let hardReflection = pow(wave, mix(13.0, 4.0, roughness));
  let blackFold = pow(1.0 - wave, mix(9.0, 3.0, roughness));
  let body = mix(wave, broadReflection, 0.2 + depth * 0.3);
  return clamp(0.018 + body * (0.46 + depth * 0.12)
               + hardReflection * (0.3 + depth * 0.42)
               - blackFold * (0.07 + depth * 0.11), 0.0, 1.0);
}

fn glsChromaticMetalSample(p: vec2<f32>, t: f32) -> vec3<f32> {
  let phase = glsChromaticMetalPhase(p, t);
  let angle = u.metalAngle * 0.01745329252;
  let brushP = glsRotate(p / max(u.metalScale, 0.05), angle);
  let brushed = sin(brushP.y * 146.0 + sin(brushP.x * 11.0) * 0.58)
              + 0.48 * sin(brushP.y * 317.0 - brushP.x * 5.0);
  let brushAmount = 0.004 + clamp(u.metalRoughness, 0.0, 1.0) * 0.014;
  let tone = clamp(glsChromaticMetalTone(phase) + brushed * brushAmount, 0.0, 1.0);
  return lqRamp(tone, u.colorD.rgb, u.colorB.rgb, u.colorC.rgb, u.colorA.rgb);
}

fn glsChromaticMetalFluid(p: vec2<f32>, t: f32) -> vec3<f32> {
  let angle = u.metalAngle * 0.01745329252;
  let splitDirection = glsRotate(vec2<f32>(0.0, 1.0), angle);
  let split = splitDirection * u.chromaticShift * 0.045;
  let redSample = glsChromaticMetalSample(p + split, t);
  let neutral = glsChromaticMetalSample(p, t);
  let blueSample = glsChromaticMetalSample(p - split, t);
  let optical = vec3<f32>(redSample.r, neutral.g, blueSample.b);
  let fringe = clamp(length(optical - neutral) * 4.0, 0.0, 1.0);
  var color = mix(neutral, optical,
                  clamp(u.chromaticShift * (0.72 + fringe * 0.28), 0.0, 1.0));
  let centerTone = glsChromaticMetalTone(glsChromaticMetalPhase(p, t));
  let glint = pow(centerTone, mix(12.0, 5.0, clamp(u.metalRoughness, 0.0, 1.0)));
  color = mix(color, u.highlightColor.rgb,
              glint * clamp(u.metalDepth, 0.0, 1.0) * 0.06);

  // A second, sphere-scale reflection layer keeps the material metallic even
  // when the optional glass shell is disabled. It modulates the animated ramp
  // instead of raising exposure, preserving dark chrome between reflections.
  let radial2 = clamp(dot(p, p), 0.0, 1.0);
  let normal = normalize(vec3<f32>(p, sqrt(max(1.0 - radial2, 0.0))));
  let roughness = clamp(u.metalRoughness, 0.0, 1.0);
  let depth = clamp(u.metalDepth, 0.0, 1.0);
  let key = pow(max(dot(normal, normalize(vec3<f32>(-0.48, 0.62, 0.62))), 0.0),
                mix(7.0, 3.0, roughness));
  let fill = pow(max(dot(normal, normalize(vec3<f32>(0.7, -0.34, 0.63))), 0.0),
                 mix(10.0, 4.0, roughness));
  let limb = 1.0 - normal.z;
  let fresnel = pow(limb, 3.0);
  let rim = pow(limb, 10.0);
  color = color * (0.86 + normal.z * 0.14);
  color = mix(color, u.highlightColor.rgb, key * (0.05 + depth * 0.13));
  color = mix(color, u.colorC.rgb, fill * (0.025 + depth * 0.07));
  color = mix(color, u.colorD.rgb, fresnel * (0.12 + depth * 0.15));
  color = mix(color, u.highlightColor.rgb, rim * (0.035 + depth * 0.055));
  return glsFinishPresetFluid(color, p);
}

fn glsOpalFluid(p: vec2<f32>, t: f32) -> vec3<f32> {
  let q = p * (0.8 + u.zoom * 0.64);
  let complexity = 0.76 + u.warp * 0.085;
  var d = -t * 0.42;
  var a = 0.0;
  for (var i: i32 = 0; i < 8; i = i + 1) {
    let fi = f32(i);
    a = a + cos(fi - d - a * q.x * complexity);
    d = d + sin(q.y * fi * complexity + a);
  }
  d = d + t * 0.42;
  let c1 = cos(q * vec2<f32>(d, a)) * 0.6 + vec2<f32>(0.4);
  let c2 = cos(a + d) * 0.5 + 0.5;
  let interference = 0.5 + 0.5 * cos(vec3<f32>(c1.x, c1.y, c2)
                         * cos(vec3<f32>(d, a, 2.5)) * 0.5 + vec3<f32>(0.5));
  let tone = fract(interference.r * 0.37 + interference.g * 0.51
                   + interference.b * 0.73 + c1.x * 0.22 - c1.y * 0.15);
  var color = lqRamp(tone, u.colorB.rgb, u.colorC.rgb, u.colorD.rgb, u.colorA.rgb);
  color = mix(color, u.colorA.rgb, 0.16 + 0.1 * interference.b);
  color = color / (vec3<f32>(1.0) + color * 0.16);
  return glsFinishPresetFluid(color, p);
}

fn glsFrostFluid(p: vec2<f32>, t: f32) -> vec3<f32> {
  // The initial frost-style orb: a slow domain warp drives broad cloudy colour
  // bodies, while a second higher-frequency field contributes adjustable veins.
  var q = p * (0.66 + u.zoom * 0.92);
  q.y = q.y + t * 0.055;
  let blur = 0.011 + 0.006 * u.zoom;
  let warpField = vec2<f32>(
    lqFbm(q * 1.14 + vec2<f32>(t * 0.055, 0.0), blur).x,
    lqFbm(q * 1.14 + vec2<f32>(6.8, -t * 0.048), blur).x
  );
  let warped = q + (warpField - vec2<f32>(0.5)) * (0.28 + u.warp * 0.17);
  let body = lqFbm(warped * 1.48 + vec2<f32>(t * 0.032, -t * 0.02), blur * 1.48);
  let veins = lqRidgeS(
    lqFbm(warped * 2.36 + vec2<f32>(3.1, -t * 0.024), blur * 2.36),
    u.sharp
  );
  let value = mix(lqStepS(body, 0.1, 0.9),
                  clamp(veins * 0.8 + body.x * 0.46, 0.0, 1.0),
                  u.ridgeAmt);
  var color = lqRamp(value, u.colorA.rgb, u.colorB.rgb, u.colorC.rgb, u.colorD.rgb);
  color = mix(color, u.colorA.rgb, 0.08 * smoothstep(0.62, 0.92, body.x));
  return glsFinishPresetFluid(color, p);
}

fn glsVoiceWaveFluid(p: vec2<f32>, t: f32) -> vec3<f32> {
  // A single broad membrane stays phase-coherent across the sphere. Nearby
  // translucent layers add volume without splitting into separate Siri bands.
  let scale = 0.76 + u.zoom * 0.34;
  let q = p / scale;
  let rimEnvelope = pow(max(1.0 - q.x * q.x, 0.0), 0.72);
  let drift = t * 0.82;
  let amplitude = 0.2 + u.warp * 0.018;
  let mainY = rimEnvelope * (amplitude * sin(q.x * 1.48 + drift)
              + 0.055 * sin(q.x * 3.2 - drift * 0.43 + 1.1));
  let distance = q.y - mainY;
  let width = 0.11 + (1.0 - u.ridgeAmt) * 0.075;
  let membrane = exp(-distance * distance / max(width * width, 0.001)) * rimEnvelope;
  let upperVeil = exp(-(distance - 0.105) * (distance - 0.105)
                      / max(width * width * 2.4, 0.001)) * rimEnvelope;
  let lowerVeil = exp(-(distance + 0.115) * (distance + 0.115)
                      / max(width * width * 2.8, 0.001)) * rimEnvelope;
  let crest = exp(-distance * distance / 0.0026) * rimEnvelope;
  let depth = sqrt(max(1.0 - clamp(dot(p, p), 0.0, 1.0), 0.0));
  var color = mix(u.colorA.rgb * 0.7, u.colorD.rgb * 0.34,
                  smoothstep(-0.82, 0.82, q.y));
  color = mix(color, u.colorB.rgb, upperVeil * 0.7);
  color = mix(color, u.colorC.rgb, lowerVeil * 0.62);
  color = color + mix(u.colorB.rgb, u.colorC.rgb, 0.46) * membrane * 0.34;
  color = color + u.highlightColor.rgb * crest * 0.14;
  color = color * (0.58 + 0.42 * depth);
  return glsFinishPresetFluid(color, p);
}

fn glsBlueDropFluid(p: vec2<f32>, t: f32) -> vec3<f32> {
  // Slow diagonal advection keeps the broad liquid bodies coherent. The two
  // shear waves replace the reference orb's circular, looped point motion.
  let depth = sqrt(max(1.0 - clamp(dot(p, p), 0.0, 1.0), 0.0));
  var q = p * mix(0.72, 1.0, depth * 0.62 + 0.38);
  q = glsRotate(q, -0.24 + 0.06 * sin(t * 0.17));
  let scale = 1.0 + u.zoom * 1.12;
  let blur = 0.012 + 0.006 * u.zoom;
  let driftA = lqFbm(q * 1.28 + vec2<f32>(t * 0.095, -t * 0.034), blur * 1.28);
  let driftB = lqFbm(glsRotate(q, 1.08) * 1.62
                     + vec2<f32>(-t * 0.042, t * 0.078), blur * 1.62);
  var flowed = q + vec2<f32>(driftA.x - 0.5, driftB.x - 0.5)
                 * (0.24 + u.warp * 0.1);
  flowed.x = flowed.x + sin(flowed.y * 2.15 + t * 0.24) * (0.035 + u.warp * 0.012);
  flowed.y = flowed.y + sin(flowed.x * 1.38 - t * 0.18) * (0.045 + u.warp * 0.01);
  let body = lqFbm(flowed * scale + vec2<f32>(t * 0.025, -t * 0.018), blur * scale);
  let marble = lqRidgeS(lqFbm(flowed * (1.72 + u.zoom * 0.9)
                              + vec2<f32>(2.7, -t * 0.035),
                              blur * (1.72 + u.zoom * 0.9)),
                            0.8 + u.sharp * 0.46);
  let value = clamp(mix(body.x, body.x * 0.62 + marble * 0.58, u.ridgeAmt), 0.0, 1.0);
  var color = lqRamp(value, u.colorA.rgb, u.colorB.rgb, u.colorC.rgb, u.colorD.rgb);
  let light = pow(max(dot(normalize(vec3<f32>(p, depth)),
                          normalize(vec3<f32>(-0.48, 0.62, 0.92))), 0.0), 3.2);
  color = mix(color, u.highlightColor.rgb, light * (0.035 + 0.05 * u.shade));
  color = color * (0.74 + 0.26 * depth);
  return glsFinishPresetFluid(color, p);
}

fn glsVioletEmberFluid(p: vec2<f32>, t: f32) -> vec3<f32> {
  // A radial twist and two crossing drift fields make heavy molten folds. This
  // moves as a breathing spiral instead of the reference orb's closed circles.
  let scale = 1.08 + u.zoom * 1.18;
  let blur = 0.011 + 0.005 * u.zoom;
  let radius = length(p);
  let twist = t * 0.055 + radius * (0.72 + u.warp * 0.11)
              + 0.08 * sin(t * 0.31 + radius * 4.0);
  let q = glsRotate(p * scale, twist);
  let low = lqFbm(q * 1.18 + vec2<f32>(t * 0.068, -t * 0.105), blur * 1.18);
  let cross = lqFbm(glsRotate(q, -1.12) * 1.52
                    + vec2<f32>(-t * 0.094, t * 0.042)
                    + vec2<f32>(low.x * 1.35, -low.x * 0.72), blur * 1.52);
  let warped = q + vec2<f32>(low.x - 0.5, cross.x - 0.5)
                   * (0.3 + u.warp * 0.12);
  let melt = lqFbm(warped * 1.34
                   + vec2<f32>(cross.x * 1.48, low.x * 1.12), blur * 1.34);
  let veins = lqRidgeS(lqFbm(warped * (2.05 + u.zoom * 0.72)
                             + vec2<f32>(-2.1, t * 0.052),
                             blur * (2.05 + u.zoom * 0.72)),
                           0.82 + u.sharp * 0.58);
  let heat = smoothstep(0.18, 0.92,
                        melt.x * (0.72 - u.ridgeAmt * 0.16)
                        + veins * (0.32 + u.ridgeAmt * 0.5));
  var color = lqRamp(heat, u.colorA.rgb, u.colorB.rgb, u.colorC.rgb, u.colorD.rgb);
  let pulse = 0.94 + 0.06 * sin(t * 0.44 + melt.x * 5.0);
  color = color * pulse;
  color = mix(color, u.highlightColor.rgb, pow(veins, 4.0) * 0.045);
  return glsFinishPresetFluid(color, p);
}

fn glsRefractiveBlobFluid(p: vec2<f32>, t: f32) -> vec3<f32> {
  // Broad advected cells give the lens something legible to bend. A slower
  // caustic ribbon crosses those cells out of phase, so the material evolves
  // without looking like a texture rotating inside a fixed sphere.
  let radial2 = clamp(dot(p, p), 0.0, 1.0);
  let depth = sqrt(max(1.0 - radial2, 0.0));
  let scale = 0.82 + u.zoom * 1.08;
  let blur = 0.012 + 0.005 * u.zoom;
  var q = glsRotate(p * scale, 0.08 * sin(t * 0.17));
  let driftA = lqFbm(q * 1.16 + vec2<f32>(t * 0.052, -t * 0.078), blur * 1.16);
  let driftB = lqFbm(glsRotate(q, 1.21) * 1.34
                     + vec2<f32>(-t * 0.064, t * 0.041), blur * 1.34);
  q = q + vec2<f32>(driftA.x - 0.5, driftB.x - 0.5)
          * (0.34 + u.warp * 0.105);

  let body = lqFbm(q * 1.42 + vec2<f32>(driftB.x * 0.82, driftA.x * 0.66),
                   blur * 1.42);
  let ribbonPhase = q.y * (2.2 + u.warp * 0.11)
                  + sin(q.x * 1.72 - t * 0.19) * 0.92
                  + sin((q.x + q.y) * 1.08 + t * 0.13) * 0.46;
  let ribbon = pow(clamp(1.0 - abs(sin(ribbonPhase)), 0.0, 1.0),
                   0.82 + u.sharp * 0.23);
  let fold = lqRidgeS(lqFbm(q * 2.05 + vec2<f32>(2.8, -t * 0.037),
                            blur * 2.05), 0.9 + u.sharp * 0.32);
  let value = clamp(body.x * 0.5 + driftA.x * 0.16
                    + ribbon * (0.2 + u.ridgeAmt * 0.2)
                    + fold * u.ridgeAmt * 0.18, 0.0, 1.0);

  var color = lqRamp(value, u.colorA.rgb, u.colorB.rgb, u.colorC.rgb, u.colorD.rgb);
  let caustic = pow(ribbon, 3.1) * (0.24 + 0.28 * u.ridgeAmt)
               + pow(fold, 4.2) * 0.08;
  color = mix(color, u.colorD.rgb, clamp(caustic, 0.0, 0.52));
  color = color * (0.7 + depth * 0.3);
  let key = pow(max(dot(normalize(vec3<f32>(p, depth)),
                        normalize(vec3<f32>(-0.42, 0.58, 0.9))), 0.0), 4.0);
  color = mix(color, u.highlightColor.rgb, key * 0.055);
  return glsFinishPresetFluid(color, p);
}

fn glsParticleRibbonFluid(p: vec2<f32>, t: f32) -> vec3<f32> {
  // The visible body is emitted by the dedicated particle pipeline. Keeping
  // this branch empty lets the shared fullscreen pass contribute only the
  // optional glass shell and its transparent background contract.
  return vec3<f32>(0.0);
}

fn glsPresetFluid(p: vec2<f32>, style: i32, t: f32) -> vec3<f32> {
  if (style == 9) { return glsSiriFluid(p, t); }
  if (style == 10) { return glsAuroraFluid(p, t); }
  if (style == 11) { return glsPlasmaFluid(p, t); }
  if (style == 12) { return glsChromeFluid(p, t); }
  if (style == 13) { return glsOpalFluid(p, t); }
  if (style == 14) { return glsSpectrumFluid(p, t); }
  if (style == 15) { return glsFrostFluid(p, t); }
  if (style == 19) { return glsVoiceWaveFluid(p, t); }
  if (style == 20) { return glsBlueDropFluid(p, t); }
  if (style == 21) { return glsVioletEmberFluid(p, t); }
  if (style == 22) { return glsChromaticMetalFluid(p, t); }
  if (style == 23) { return glsRefractiveBlobFluid(p, t); }
  if (style == 24) { return glsParticleRibbonFluid(p, t); }
  return glsFrostFluid(p, t);
}

// ---------------------------------------------------------------------------
// The fluid, at one point, already blurred and straight (not premultiplied):
// the sheet's shader on \`fu\` — both programs, all four inner branches, and the
// shared shade tail — with the blur folded into the noise bank as above. The
// disc's own alpha is the caller's, because it is analytic now.
// ---------------------------------------------------------------------------
fn glsFluid(fu: vec2<f32>, md: i32, t: f32) -> vec3<f32> {
  let df = length(fu);

  let cA = u.colorA.rgb;
  let cB = u.colorB.rgb;
  let cC = u.colorC.rgb;
  let cD = u.colorD.rgb;

  // The blur's sigma, carried from fluid units into the fluid's own domains.
  // \`sp\` is it in pp/q units — the warp shifts q about but does not stretch it
  // on average, so pp and q share one. \`sw\` is the warp field's own, softened
  // by GL_KWA.
  let blurSigma = select(GL_BSIG_CLEAR, GL_BSIG_GLASS, u.glassEnabled > 0.5);
  let sp = blurSigma * u.zoom;
  let sw = sp * 1.1 * GL_KWA;

  var fcol: vec3<f32>;
  if (md < 0) {
    // progA — the warped body, the only branch with the slow vertical drift
    // and the only one that reads Ridge.
    var pp = fu * u.zoom;
    pp.y = pp.y + t * 0.05;
    let w = vec2<f32>(lqFbm(pp * 1.1 + vec2<f32>(0.0, t * 0.09), sw).x,
                      lqFbm(pp * 1.1 + vec2<f32>(7.7, -t * 0.07), sw).x);
    let q = pp + u.warp * (w - vec2<f32>(0.5));
    let body  = lqFbm(q * 1.5 + vec2<f32>(t * 0.04, 0.0), sp * 1.5);
    let veins = lqRidgeS(lqFbm(q * 2.2 + vec2<f32>(3.1), sp * 2.2), u.sharp);
    let v = mix(lqStepS(body, 0.12, 0.88),
                clamp(veins * 0.85 + 0.45 * body.x, 0.0, 1.0), u.ridgeAmt);
    fcol = lqRamp(v, cA, cB, cC, cD);
  } else {
    // progB — same warp, no vertical drift, four inner branches.
    let pp = fu * u.zoom;
    let w = vec2<f32>(lqFbm(pp * 1.1 + vec2<f32>(0.0, t * 0.09), sw).x,
                      lqFbm(pp * 1.1 + vec2<f32>(7.7, -t * 0.07), sw).x);
    let q = pp + u.warp * (w - vec2<f32>(0.5));
    if (md == 0) {
      // Nectar — a sine band the noise leans on. The fbm is INSIDE the sine, so
      // the removed detail integrates out in closed form rather than by
      // quadrature: E[sin(A + 6e)] = sin(A)·exp(-18·sd²). The second term of
      // the exponent is the same integral for the sine's own \`q.x * 7.0\`, which
      // the blur attenuates by exp(-49·sp²/2).
      let n0 = lqFbm(q * 2.2, sp * 2.2);
      let damp = exp(-18.0 * n0.y * n0.y - 24.5 * sp * sp);
      var v = 0.5 + 0.5 * damp * sin(q.x * 7.0 + n0.x * 6.0 + t * 0.35);
      v = mix(v, lqFbm(q * 1.4 + vec2<f32>(t * 0.03), sp * 1.4).x, 0.25);
      fcol = lqRamp(v, cA, cB, cC, cD);
    } else if (md == 1) {
      // Lumen — two ridged fields multiplied into filaments. The two fields are
      // independent, so each integrates its own detail out before the product.
      let v = lqRidgeS(lqFbm(q * 1.4 + vec2<f32>(t * 0.06, 0.0), sp * 1.4), u.sharp)
            * lqRidgeS(lqFbm(q * 1.7 - vec2<f32>(0.0, t * 0.05), sp * 1.7), u.sharp);
      fcol = lqRamp(pow(v, 0.7), cA, cB, cC, cD);
    } else if (md == 6) {
      // Sprig — noise warped by noise, with a ridged edge darkening it.
      let v = lqFbm(q * 1.3 + vec2<f32>(1.5 * lqFbm(q * 2.6 + vec2<f32>(t * 0.025), sp * 2.6).x), sp * 1.3);
      let edge = lqRidgeS(lqFbm(q * 2.1 + vec2<f32>(7.0), sp * 2.1), 1.3);
      fcol = lqRamp(lqStepS(v, 0.1, 0.9), cA, cB, cC, cD);
      fcol = fcol * (1.0 - 0.18 * edge);
    } else {
      // Haze and Smoke — the same rising plume at two palettes.
      let q2 = q + vec2<f32>(0.0, -t * 0.14);
      let v = lqFbm(q2 * 1.6 + vec2<f32>(2.2 * lqFbm(q2 * 2.4 + vec2<f32>(0.0, -t * 0.05), sp * 2.4).x), sp * 1.6);
      fcol = lqRamp(lqPowS(v, 1.5), cA, cB, cC, cD);
    }
  }

  // The sheet's shared tail: a highlight up-left, a shadow down-right, and a
  // darkened limb. All three are far below the blur's cutoff, so they are the
  // sheet's own expressions untouched. The grain term the sheet ends on is not
  // ported — see the header. The two \`1 - shade*k*smoothstep(...)\` terms are
  // multiplicative darkening, not colours, so they stay literal.
  fcol = mix(fcol, u.highlightColor.rgb,
             u.shade * 0.3 * smoothstep(0.25, 1.25, dot(fu, vec2<f32>(-0.32, 0.78))));
  fcol = fcol * (1.0 - u.shade * 0.42 * smoothstep(-0.05, 1.25, dot(fu, vec2<f32>(0.45, -0.62))));
  fcol = fcol * (1.0 - u.shade * 0.3 * smoothstep(0.72, 1.0, df));
  return clamp(fcol, vec3<f32>(0.0), vec3<f32>(1.0));
}

// ---------------------------------------------------------------------------
// The shell.
// ---------------------------------------------------------------------------

// Source-over onto an opaque destination, straight (un-premultiplied) sRGB.
fn glsOver(dst: vec3<f32>, src: vec3<f32>, a: f32) -> vec3<f32> {
  let k = clamp(a, 0.0, 1.0);
  return src * k + dst * (1.0 - k);
}

fn glsRefractionProfile(t: f32) -> f32 {
  let depth = clamp(t, 0.0, 1.0);
  let circular = sqrt(max(1.0 - (1.0 - depth) * (1.0 - depth), 0.0));
  return 1.0 - circular;
}

fn glsHighlightLobe(normal: vec2<f32>, direction: vec2<f32>, cut: f32,
                     power: f32) -> f32 {
  let angular = clamp((dot(normal, direction) - cut) / max(1.0 - cut, 0.001),
                      0.0, 1.0);
  return pow(angular, power);
}

fn glsContourWave(angle: f32, t: f32) -> vec2<f32> {
  let style = i32(u.style + 0.5);
  if (style == 19) {
    let wave = sin(angle * 2.0 + t * 0.27) * 0.72
               + sin(angle * 4.0 - t * 0.16 + 2.1) * 0.28;
    let slope = cos(angle * 2.0 + t * 0.27) * 1.44
                + cos(angle * 4.0 - t * 0.16 + 2.1) * 1.12;
    return vec2<f32>(wave, slope);
  }
  let wave = sin(angle * 3.0 + t * 0.62) * 0.52
             + sin(angle * 5.0 - t * 0.41 + 1.7) * 0.31
             + sin(angle * 2.0 + t * 0.23 + 3.1) * 0.17;
  let slope = cos(angle * 3.0 + t * 0.62) * 1.56
              + cos(angle * 5.0 - t * 0.41 + 1.7) * 1.55
              + cos(angle * 2.0 + t * 0.23 + 3.1) * 0.34;
  return vec2<f32>(wave, slope);
}

fn glsContourStrength() -> f32 {
  if (u.style >= 18.5) { return 0.11; }
  return select(0.09, 0.16, u.style >= 15.5);
}

fn glsContourScale(uv: vec2<f32>, t: f32, amount: f32) -> f32 {
  if (amount <= 0.0) { return 1.0; }
  let contour = glsContourWave(atan2(uv.y, uv.x), t);
  return 1.0 + clamp(amount, 0.0, 1.0) * glsContourStrength() * contour.x;
}

fn glsContourNormal(uv: vec2<f32>, rad: f32, t: f32, amount: f32) -> vec2<f32> {
  let distance = length(uv);
  if (distance <= 0.0001) { return vec2<f32>(0.0); }
  let radial = uv / distance;
  let contour = glsContourWave(atan2(uv.y, uv.x), t);
  let slope = clamp(amount, 0.0, 1.0) * glsContourStrength() * contour.y;
  let tangent = vec2<f32>(-radial.y, radial.x);
  return normalize(radial - tangent * (rad * slope / distance));
}

fn glsRefractionNormal(base: vec2<f32>, p: vec2<f32>, t: f32,
                       style: i32) -> vec2<f32> {
  if (style != 23) { return base; }
  let tangent = vec2<f32>(-base.y, base.x);
  let a = lqFbm(p * 2.15 + vec2<f32>(t * 0.061, -t * 0.043), 0.018).x;
  let b = lqFbm(glsRotate(p, 1.37) * 2.55
                  + vec2<f32>(-t * 0.037, t * 0.052), 0.021).x;
  let wave = (a - b) * 0.76 + sin(atan2(p.y, p.x) * 3.0 + t * 0.21) * 0.08;
  return normalize(base + tangent * wave);
}

fn orbGlassLiquidAnim(uv01: vec2<f32>) -> vec4<f32> {
  // The runner hands uv01 with y down from the top, like stitchable MSL's
  // \`position\`; the orb was authored bottom-left, so flip back.
  let fc = vec2<f32>(uv01.x, 1.0 - uv01.y) * u.size;
  let uv = (2.0 * fc - u.size) / max(min(u.size.x, u.size.y), 1.0);

  let rad = max(u.radius, 0.05);
  let t = u.time * u.speed;
  let s = i32(u.style + 0.5);
  let emissionOnly = u.glassEnabled <= 0.5 && (s == 9 || s == 14 || s == 24);
  let contourRad = rad * glsContourScale(uv, t, u.contourDeform);

  // Nothing on this pixel — and here that is the whole fluid and the whole
  // shell skipped, over roughly 60% of the quad. 1.01 is the far edge of the
  // ball's own coverage, \`1 - smoothstep(0.99, 1.01, pd)\` on the last line of
  // this function, which is EXACTLY zero past it, so the full path already
  // returns opaque black here. An early-out, not a clip: the number is that
  // coverage term's own far edge, so do not "tidy" it to 1.0 — that would
  // shave the outer half of the limb's antialiasing.
  //
  // Tested on \`uv\` rather than on \`pd\` because \`|uv| > rad * 1.01\` IS
  // \`pd > 1.01\`, and it keeps \`p\` and \`pd\` in the same basic block as
  // everything that reads them — the shape the four sibling orbs of this port
  // need, where branching on \`d\` after computing it makes the compiler stop
  // folding \`uv / rad\` into its uses and the moved last bit comes back through
  // their grain hash as speckle up to 34/255. Glass Liquid has no grain and is
  // nearly immune either way: at 1024x1024 this costs under a dozen bytes of a
  // four-million-byte frame, off by 1/255. Those are the branch existing, not a
  // pixel wrongly skipped — a copy of this guard with a threshold it can never
  // reach diffs identically, and against it the guard is exactly 0/255.
  if (length(uv) > contourRad * (1.01 + mfEdgeD(u.edgeSoftness))) {
    // Off the ball entirely — but the halo lives out here, so hand back
    // what the edge bank paints on nothing. Exactly black at Glow 0.
    let halo = clamp(mfEdgeGlow(vec3<f32>(0.0), uv, vec2<f32>(0.0), contourRad,
                                u.edgeSoftness, u.edgeGlow, u.glowColor.rgb),
                     vec3<f32>(0.0), vec3<f32>(1.0));
    let haloAlpha = max(halo.r, max(halo.g, halo.b));
    return vec4<f32>(halo, haloAlpha);
  }

  let p   = uv / contourRad;     // deformed ball space: |p| == 1 on the edge
  let pd  = length(p);

  // ---- the fluid ------------------------------------------------------
  let fu = p / GL_FU;

  // Branch dispatch. Source indices 0/2/4/6 are progA (md < 0); the others are
  // progB at the sheet's own mode number. An if-chain avoids a runtime-indexed
  // lookup here.
  var md: i32 = -1;
  if (s == 1) { md = 1; }
  else if (s == 3 || s == 8) { md = 7; }
  else if (s == 5) { md = 6; }
  else if (s == 7) { md = 0; }

  let clearFa = 1.0 - smoothstep(GL_CLEAR_EA, GL_CLEAR_EB, pd);
  let contourNormal = glsContourNormal(uv, rad, t, u.contourDeform);
  let normal = glsRefractionNormal(contourNormal, p, t, s);
  let edgeDepth = max(1.0 - pd, 0.0);
  let refractionWidth = 0.015 + 0.95 * clamp(u.shellMidAlpha, 0.0, 1.0);
  let refractionT = edgeDepth / max(refractionWidth, 0.001);
  let refractionProfile = pow(glsRefractionProfile(refractionT), 0.68);
  let refractionAmount = 1.6 * clamp(u.glassOpacity, 0.0, 1.0)
                         * refractionProfile;
  let refractedP = p - normal * refractionAmount;
  var fcol = vec3<f32>(0.0);
  if (clearFa > 0.0) {
    if (s >= 9) {
      if (u.glassEnabled > 0.5) {
        // Three actual fluid evaluations produce optical dispersion. At the
        // outer boundary the reference lens pulls samples from deep inside the
        // orb; the channels converge continuously at the inner edge of the
        // refraction band.
        let channelSplit = 0.14 * clamp(u.gloss, 0.0, 2.0)
                           * clamp(u.glassOpacity, 0.0, 1.0)
                           * refractionProfile;
        let redSample = glsPresetFluid(refractedP - normal * channelSplit, s, t);
        let greenSample = glsPresetFluid(refractedP, s, t);
        let blueSample = glsPresetFluid(refractedP + normal * channelSplit, s, t);
        fcol = vec3<f32>(redSample.r, greenSample.g, blueSample.b);
      }
      else { fcol = glsPresetFluid(p, s, t); }
    }
    else { fcol = glsFluid(fu, md, t); }
  }

  // Voice-like presets become a true emissive layer when glass is disabled.
  // Their empty pixels no longer inherit the opaque circular canvas fill.
  let lum = dot(fcol, vec3<f32>(0.213, 0.715, 0.072));
  let clearSat = clamp(vec3<f32>(lum) + (fcol - vec3<f32>(lum)) * 1.22,
                       vec3<f32>(0.0), vec3<f32>(1.0));
  let particleGlassOverlay = s == 24;
  var col = select(
    glsOver(u.canvasColor.rgb, clearSat, 0.99 * clearFa),
    vec3<f32>(0.0),
    particleGlassOverlay,
  );
  if (emissionOnly) {
    let signal = max(clearSat.r, max(clearSat.g, clearSat.b));
    let emissionCoverage = smoothstep(0.025, 0.16, signal);
    col = clearSat * emissionCoverage;
  }
  if (u.glassEnabled > 0.5) {
    // Surface lighting stays on a thin arc. The broad visual change comes from
    // the refracted fluid above, not from a translucent white overlay.
    // Its weights still need enough contrast to keep the exposed colour and
    // highlight controls perceptible in the compact scene preview.
    let surfaceWidth = select(
      0.026 + 0.055 * clamp(u.shellEdgeAlpha, 0.0, 1.0),
      0.09 + 0.12 * clamp(u.shellEdgeAlpha, 0.0, 1.0),
      particleGlassOverlay,
    );
    let surfaceBand = (1.0 - smoothstep(0.0, surfaceWidth, edgeDepth)) * clearFa;
    let opticalRim = pow(surfaceBand, select(1.8, 1.3, particleGlassOverlay));
    let innerRimAlpha = select(
      opticalRim * u.glassOpacity * 0.45,
      opticalRim * u.glassOpacity * 0.14,
      particleGlassOverlay,
    );
    col = glsOver(col, u.shellInner.rgb, innerRimAlpha);

    let coolDirection = normalize(vec2<f32>(0.84, 0.54));
    let warmDirection = normalize(vec2<f32>(-0.62, -0.78));
    let coolSplit = glsHighlightLobe(normal, coolDirection, -0.32, 1.8);
    let warmSplit = glsHighlightLobe(normal, warmDirection, -0.28, 2.0);
    let dispersion = opticalRim * clamp(u.gloss, 0.0, 2.0)
                     * (0.8 + 0.8 * u.shellEdgeAlpha);
    col = glsOver(col, u.shellMid.rgb, dispersion * coolSplit);
    col = glsOver(col, u.shellEdge.rgb, dispersion * warmSplit);

    let edgeShadow = opticalRim * (0.015 + 0.15 * u.shellEdgeAlpha)
                     * (0.15 + 0.85 * max(dot(normal, vec2<f32>(0.45, -0.89)), 0.0));
    col = col * (1.0 - edgeShadow);

    let keyDirection = normalize(vec2<f32>(-0.68, 0.73));
    let fillDirection = normalize(vec2<f32>(0.74, -0.67));
    let key = opticalRim * glsHighlightLobe(normal, keyDirection, 0.2, 2.8)
              * clamp(u.sheen, 0.0, 2.0) * 1.4;
    let fill = opticalRim * glsHighlightLobe(normal, fillDirection, 0.4, 3.6)
               * clamp(u.sheen, 0.0, 2.0) * 1.0;
    col = glsOver(col, u.sheenColor.rgb, key);
    col = glsOver(col, u.specColor.rgb, fill);
  }

  // The ball's own edge, and nothing outside it — everything the effect does
  // not paint must be exactly 0 so the page shows through.
  let ballA = 1.0 - smoothstep(0.99 - mfEdgeD(u.edgeSoftness), 1.01 + mfEdgeD(u.edgeSoftness), pd);
  col = clamp(col * max(u.exposure, 0.0), vec3<f32>(0.0), vec3<f32>(1.0)) * ballA;
  // The Orbs edge bank — the Edge group's Glow. Adding zero is exactly
  // the render this file was diffed against, and zero is the default.
  let edged = mfEdgeGlow(col, uv, vec2<f32>(0.0), contourRad,
                         u.edgeSoftness, u.edgeGlow, u.glowColor.rgb);
  let finalColor = clamp(edged, vec3<f32>(0.0), vec3<f32>(1.0));
  let emissionAlpha = max(finalColor.r, max(finalColor.g, finalColor.b));
  let sphereAlpha = clamp(max(ballA, emissionAlpha), 0.0, 1.0);
  let finalAlpha = select(
    sphereAlpha,
    emissionAlpha,
    emissionOnly || particleGlassOverlay,
  );
  return vec4<f32>(finalColor, finalAlpha);
}


struct VOut {
  @builtin(position) pos: vec4<f32>,
  @location(0) uv: vec2<f32>,
};

@vertex
fn vs_main(@builtin(vertex_index) i: u32) -> VOut {
  var p = array<vec2<f32>, 3>(
    vec2<f32>(-1.0, -1.0),
    vec2<f32>( 3.0, -1.0),
    vec2<f32>(-1.0,  3.0),
  );
  var out: VOut;
  out.pos = vec4<f32>(p[i], 0.0, 1.0);
  let uv01 = (p[i] + vec2<f32>(1.0)) * 0.5;
  out.uv = vec2<f32>(uv01.x, 1.0 - uv01.y);
  return out;
}

@fragment
fn fs_main(in: VOut) -> @location(0) vec4<f32> {
  let c = orbGlassLiquidAnim(in.uv);

  let fc = vec2<f32>(in.uv.x, 1.0 - in.uv.y) * u.size;
  let uv = (2.0 * fc - u.size) / max(min(u.size.x, u.size.y), 1.0);
  let rad = max(u.radius, 0.05);
  let t = u.time * u.speed;
  let contourRad = rad * glsContourScale(uv, t, u.contourDeform);
  let q = (2.0 * fc - u.size) / u.size;
  let fitEnd = 1.0;
  let fitFeather = 2.0 / max(min(u.size.x, u.size.y), 1.0);
  let fitStart = min(mix(contourRad, fitEnd, 0.5), fitEnd - fitFeather);
  let fit = 1.0 - smoothstep(fitStart, fitEnd, max(abs(q.x), abs(q.y)));
  return vec4<f32>(c.rgb * fit, c.a * fit);
}

const PR_U_SEGMENTS: u32 = 384u;
const PR_V_SEGMENTS: u32 = 96u;
const PR_PARTICLES_PER_LAYER: u32 = PR_U_SEGMENTS * PR_V_SEGMENTS;

struct RibbonOut {
  @builtin(position) pos: vec4<f32>,
  @location(0) local: vec2<f32>,
  @location(1) color: vec3<f32>,
  @location(2) opacity: f32,
};

fn prHash(value: f32) -> f32 {
  return fract(sin(value * 12.9898 + 78.233) * 43758.5453);
}

fn prRotateX(p: vec3<f32>, angle: f32) -> vec3<f32> {
  let c = cos(angle);
  let s = sin(angle);
  return vec3<f32>(p.x, c * p.y - s * p.z, s * p.y + c * p.z);
}

fn prRotateY(p: vec3<f32>, angle: f32) -> vec3<f32> {
  let c = cos(angle);
  let s = sin(angle);
  return vec3<f32>(c * p.x + s * p.z, p.y, -s * p.x + c * p.z);
}

fn prCurve(theta: f32, layer: f32, phase: f32) -> vec3<f32> {
  let local = theta + layer * 0.11;
  let foldPhase = 2.0 * local + phase * (0.72 + layer * 0.025);
  let fold = clamp(u.ribbonFold, 0.0, 1.2);
  let radial = 0.4 + (0.085 + fold * 0.04) * cos(foldPhase);
  let orbit = local + phase * 0.13
              + sin(local - phase * 0.22 + layer) * fold * 0.13;
  let vertical = (0.235 + fold * 0.085) * sin(foldPhase)
                 + 0.055 * sin(local * 3.0 - phase * 0.46 + layer * 0.7);
  return vec3<f32>(radial * cos(orbit), vertical, radial * sin(orbit));
}

fn prPalette(valueIn: f32) -> vec3<f32> {
  let value = fract(valueIn) * 4.0;
  if (value < 1.0) { return mix(u.colorA.rgb, u.colorB.rgb, value); }
  if (value < 2.0) { return mix(u.colorB.rgb, u.colorC.rgb, value - 1.0); }
  if (value < 3.0) { return mix(u.colorC.rgb, u.colorD.rgb, value - 2.0); }
  return mix(u.colorD.rgb, u.colorA.rgb, value - 3.0);
}

@vertex
fn ribbon_vs_main(
  @builtin(vertex_index) vertexIndex: u32,
  @builtin(instance_index) instanceIndex: u32,
) -> RibbonOut {
  var corners = array<vec2<f32>, 6>(
    vec2<f32>(-1.0, -1.0), vec2<f32>(1.0, -1.0), vec2<f32>(-1.0, 1.0),
    vec2<f32>(-1.0, 1.0), vec2<f32>(1.0, -1.0), vec2<f32>(1.0, 1.0),
  );
  let layerIndex = instanceIndex / PR_PARTICLES_PER_LAYER;
  let particleIndex = instanceIndex % PR_PARTICLES_PER_LAYER;
  let uIndex = particleIndex / PR_V_SEGMENTS;
  let vIndex = particleIndex % PR_V_SEGMENTS;
  let layer = f32(layerIndex);
  let random = prHash(f32(instanceIndex));
  let activeLayer = layer < floor(clamp(u.ribbonCount, 2.0, 6.0) + 0.5);

  let uCoord = (f32(uIndex) + prHash(f32(instanceIndex) + 11.0) * 0.56)
               / f32(PR_U_SEGMENTS);
  let vCoord = (f32(vIndex) + prHash(f32(instanceIndex) + 29.0) * 0.46)
               / f32(PR_V_SEGMENTS);
  let strip = vCoord * 2.0 - 1.0;
  let t = u.time * u.speed;
  let phase = t * 0.48;
  let arc = fract(uCoord + layer * 0.211 - phase * 0.019);
  let arcLength = 0.76 + 0.055 * sin(t * 0.23 + layer * 1.71);
  let arcPosition = arc / arcLength;
  let arcEnvelope = smoothstep(0.0, 0.075, arcPosition)
                    * (1.0 - smoothstep(0.88, 1.0, arcPosition));
  let particleVisible = activeLayer
                        && arc <= arcLength
                        && random <= clamp(u.particleDensity, 0.2, 1.0);
  let theta = uCoord * 6.28318530718;
  let center = prCurve(theta, layer, phase);
  let ahead = prCurve(theta + 0.006, layer, phase);
  let tangent = normalize(ahead - center);
  let radial = normalize(center + vec3<f32>(0.001, 0.013, 0.007));
  let side = normalize(cross(tangent, radial));
  let surfaceNormal = normalize(cross(side, tangent));
  let twist = theta * (0.72 + u.ribbonTwist * 0.58)
              + phase * 0.74 + layer * 1.17;
  let ribbonDirection = normalize(side * cos(twist) + surfaceNormal * sin(twist));
  let widthEnvelope = (0.72 + 0.28 * pow(sin(theta * 1.5 + phase + layer), 2.0))
                      * mix(0.42, 1.0, sqrt(max(arcEnvelope, 0.0)));
  var position = center + ribbonDirection * strip * u.ribbonWidth * 0.5 * widthEnvelope;

  let pulse = sin(t * 0.73 + layer * 1.71)
              + 0.44 * sin(t * 1.17 + layer * 0.83 + 1.2);
  position *= 1.0 + u.ribbonBreath * pulse * 0.16;
  let layerCenter = layer
                    - (floor(clamp(u.ribbonCount, 2.0, 6.0) + 0.5) - 1.0) * 0.5;
  position = prRotateY(
    position,
    layerCenter * 0.24 + sin(t * 0.19 + layer * 1.3) * 0.055,
  );
  position = prRotateX(
    position,
    layerCenter * 0.14 + cos(t * 0.17 + layer * 0.9) * 0.04,
  );
  position = prRotateY(position, t * 0.105 + sin(t * 0.21) * 0.11);
  position = prRotateX(position, -0.2 + sin(t * 0.16 + layer * 0.1) * 0.16);

  let minSize = max(min(u.size.x, u.size.y), 1.0);
  let depthScale = 0.88 + position.z * 0.16;
  let orbPosition = position.xy * u.radius * 1.45 * depthScale;
  let clip = vec2<f32>(
    orbPosition.x * minSize / max(u.size.x, 1.0),
    orbPosition.y * minSize / max(u.size.y, 1.0),
  );
  let canvasParticleScale = clamp(minSize / 640.0, 0.22, 1.0);
  let pointPixels = max(0.6, u.particleSize)
                    * (1.5 + u.particleBloom * 2.5)
                    * (0.92 + position.z * 0.18)
                    * canvasParticleScale;
  let corner = corners[vertexIndex];
  let pointOffset = corner * pointPixels * 2.0 / max(u.size, vec2<f32>(1.0));

  let colorPhase = uCoord * 0.32 + layer * 0.19 + phase * 0.025
                   + position.z * 0.08;
  let stripEdge = smoothstep(0.58, 1.0, abs(strip));
  let front = clamp(0.78 + position.z * 0.54, 0.5, 1.24);
  let baseOpacity = mix(0.025, 0.009, clamp(u.shade / 1.5, 0.0, 1.0));
  var out: RibbonOut;
  out.pos = select(
    vec4<f32>(2.0, 2.0, 1.0, 1.0),
    vec4<f32>(clip + pointOffset, clamp(0.5 - position.z * 0.12, 0.05, 0.95), 1.0),
    particleVisible,
  );
  out.local = corner;
  out.color = pow(
    mix(prPalette(colorPhase), u.highlightColor.rgb, stripEdge * 0.56),
    vec3<f32>(0.72),
  ) * front;
  out.opacity = select(
    0.0,
    baseOpacity
      * (0.72 + stripEdge * 1.28)
      * arcEnvelope
      * pow(canvasParticleScale, 1.35),
    particleVisible,
  );
  return out;
}

@fragment
fn ribbon_fs_main(in: RibbonOut) -> @location(0) vec4<f32> {
  let distanceSquared = dot(in.local, in.local);
  if (distanceSquared > 1.0) { discard; }
  let core = exp(-distanceSquared * 4.8);
  let halo = exp(-distanceSquared * 1.35);
  let bloom = clamp(u.particleBloom, 0.0, 2.0);
  let intensity = in.opacity * (core * 1.9 + halo * bloom * 0.72)
                  * max(u.exposure, 0.0);
  let glowMix = clamp((halo - core * 0.45) * (0.18 + u.edgeGlow * 0.5), 0.0, 0.7);
  let color = mix(in.color, u.glowColor.rgb, glowMix);
  let alpha = clamp(intensity, 0.0, 1.0);
  return vec4<f32>(color * alpha, alpha);
}

@group(0) @binding(1) var ribbonTexture: texture_2d<f32>;
@group(0) @binding(2) var ribbonSampler: sampler;

fn prTextureUvFromOrb(p: vec2<f32>, contourRad: f32) -> vec2<f32> {
  let minSize = max(min(u.size.x, u.size.y), 1.0);
  let fc = (p * contourRad * minSize + u.size) * 0.5;
  return clamp(
    vec2<f32>(fc.x / max(u.size.x, 1.0), 1.0 - fc.y / max(u.size.y, 1.0)),
    vec2<f32>(0.0),
    vec2<f32>(1.0),
  );
}

fn prSampleRibbon(p: vec2<f32>, contourRad: f32) -> vec4<f32> {
  return textureSampleLevel(
    ribbonTexture,
    ribbonSampler,
    prTextureUvFromOrb(p, contourRad),
    0.0,
  );
}

@fragment
fn ribbon_composite_fs_main(in: VOut) -> @location(0) vec4<f32> {
  let direct = textureSampleLevel(ribbonTexture, ribbonSampler, in.uv, 0.0);
  if (u.glassEnabled <= 0.5) { return direct; }

  let fc = vec2<f32>(in.uv.x, 1.0 - in.uv.y) * u.size;
  let minSize = max(min(u.size.x, u.size.y), 1.0);
  let uv = (2.0 * fc - u.size) / minSize;
  let rad = max(u.radius, 0.05);
  let t = u.time * u.speed;
  let contourRad = rad * glsContourScale(uv, t, u.contourDeform);
  let shell = orbGlassLiquidAnim(in.uv);
  if (length(uv) > contourRad * (1.01 + mfEdgeD(u.edgeSoftness))) {
    return shell;
  }

  let p = uv / contourRad;
  let pd = length(p);
  let clearFa = 1.0 - smoothstep(GL_CLEAR_EA, GL_CLEAR_EB, pd);
  let normal = glsContourNormal(uv, rad, t, u.contourDeform);
  let edgeDepth = max(1.0 - pd, 0.0);
  let refractionWidth = 0.015 + 0.95 * clamp(u.shellMidAlpha, 0.0, 1.0);
  let refractionT = edgeDepth / max(refractionWidth, 0.001);
  let refractionProfile = pow(glsRefractionProfile(refractionT), 0.68);
  let refractionAmount = 1.6 * clamp(u.glassOpacity, 0.0, 1.0)
                         * refractionProfile;
  let refractedP = p - normal * refractionAmount;
  let channelSplit = 0.14 * clamp(u.gloss, 0.0, 2.0)
                     * clamp(u.glassOpacity, 0.0, 1.0)
                     * refractionProfile;
  let redSample = prSampleRibbon(refractedP - normal * channelSplit, contourRad);
  let greenSample = prSampleRibbon(refractedP, contourRad);
  let blueSample = prSampleRibbon(refractedP + normal * channelSplit, contourRad);
  let refractedAlpha = max(redSample.a, max(greenSample.a, blueSample.a)) * clearFa;
  let refracted = vec4<f32>(
    vec3<f32>(redSample.r, greenSample.g, blueSample.b) * clearFa,
    refractedAlpha,
  );
  return vec4<f32>(
    shell.rgb + refracted.rgb * (1.0 - shell.a),
    shell.a + refracted.a * (1.0 - shell.a),
  );
}
`;function fy(e){let t=[];for(let n=0;n<e.length;n+=8)t.push(`    ${e.slice(n,n+8).join(`, `)},`);return t.join(`
`)}function py(e){return{idle:zv(ty(e,`idle`)),thinking:zv(ty(e,`thinking`))}}function my(e,t){let n=py(e),r=JSON.stringify(dy);return`<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="icon" href="data:," />
  <title>Liquid Orb</title>
  <style>
    html, body, canvas { width: 100%; height: 100%; margin: 0; }
    body { overflow: hidden; background: ${e.shared.canvasColor}; }
    canvas { display: block; }
    #status { position: fixed; inset: 0; display: grid; place-items: center; color: white; font: 14px system-ui; }
  </style>
</head>
<body>
  <canvas id="orb" aria-label="Animated liquid glass orb"></canvas>
  <div id="status" hidden></div>
  <script type="module">
    const shaderSource = ${r};
    const stateSeeds = ${JSON.stringify(n)};
    const ribbonStyleIndex = ${Pv.particleRibbon};
    const ribbonInstanceCount = ${Bv};
    const activationDurationMs = ${e.activationDuration*1e3};
    const settleDurationMs = ${e.transitionDuration*1e3};
    const canvas = document.querySelector("#orb");
    const status = document.querySelector("#status");
    let animationFrame = 0;
    let device = null;
    let ribbonTarget = null;
    let stopped = false;
    let state = ${JSON.stringify(t)};
    let transitionTargetState = state;
    let fromUniforms = new Float32Array(stateSeeds[state]);
    let targetUniforms = new Float32Array(stateSeeds[state]);
    const displayedUniforms = new Float32Array(stateSeeds[state]);
    let transitionStartedAt = 0;
    let activeTransitionDuration = 0;
    let lastFrameAt = null;
    let motionPhase = 0;

    function srgbToLinear(value) {
      return value <= 0.04045
        ? value / 12.92
        : ((value + 0.055) / 1.055) ** 2.4;
    }

    function linearToSrgb(value) {
      return value <= 0.0031308
        ? value * 12.92
        : 1.055 * value ** (1 / 2.4) - 0.055;
    }

    function mixSrgb(from, to, progress) {
      return linearToSrgb(
        srgbToLinear(from) + (srgbToLinear(to) - srgbToLinear(from)) * progress,
      );
    }

    function transitionProgress(now) {
      if (activeTransitionDuration === 0) return 1;
      const raw = Math.min(1, Math.max(0, (now - transitionStartedAt) / activeTransitionDuration));
      return transitionTargetState === "thinking"
        ? 1 - (1 - raw) ** 3
        : raw * raw * (3 - 2 * raw);
    }

    function sampleTransition(now) {
      const progress = transitionProgress(now);
      for (let index = 3; index < displayedUniforms.length; index += 1) {
        const colorComponent = index >= 40
          && (index - 40) % 4 < 3;
        displayedUniforms[index] = colorComponent
          ? mixSrgb(fromUniforms[index], targetUniforms[index], progress)
          : fromUniforms[index] + (targetUniforms[index] - fromUniforms[index]) * progress;
      }
      return displayedUniforms;
    }

    function setState(nextState) {
      if (!Object.prototype.hasOwnProperty.call(stateSeeds, nextState)) {
        throw new TypeError(\`Unknown liquid orb state: \${nextState}\`);
      }
      if (nextState === state) return;

      const now = performance.now();
      sampleTransition(now);
      fromUniforms = new Float32Array(displayedUniforms);
      targetUniforms = new Float32Array(stateSeeds[nextState]);
      transitionTargetState = nextState;
      transitionStartedAt = now;
      activeTransitionDuration = nextState === "thinking"
        ? activationDurationMs
        : settleDurationMs;
      state = nextState;
    }

    Object.defineProperty(window, "liquidOrb", {
      value: Object.freeze({
        getState: () => state,
        setState,
      }),
    });

    function stopWithError(error) {
      if (stopped) return;
      stopped = true;
      cancelAnimationFrame(animationFrame);
      ribbonTarget?.destroy();
      device?.destroy();
      status.hidden = false;
      status.textContent = error instanceof Error ? error.message : String(error);
      console.error(error);
    }

    async function start() {
      if (!navigator.gpu) throw new Error("WebGPU is not supported in this environment.");
      const adapter = await navigator.gpu.requestAdapter();
      if (!adapter) throw new Error("No compatible WebGPU adapter was found.");
      device = await adapter.requestDevice();
      const context = canvas.getContext("webgpu");
      if (!context) throw new Error("Unable to create a WebGPU canvas context.");

      const format = navigator.gpu.getPreferredCanvasFormat();
      context.configure({ device, format, alphaMode: "premultiplied" });
      const shader = device.createShaderModule({ code: shaderSource });
      const compilation = await shader.getCompilationInfo();
      const errors = compilation.messages.filter((message) => message.type === "error");
      if (errors.length) {
        throw new Error(errors.map((message) => \`\${message.lineNum}:\${message.linePos} \${message.message}\`).join("\\n"));
      }

      const pipeline = device.createRenderPipeline({
        layout: "auto",
        vertex: { module: shader, entryPoint: "vs_main" },
        fragment: {
          module: shader,
          entryPoint: "fs_main",
          targets: [{
            format,
            blend: {
              color: {
                srcFactor: "one",
                dstFactor: "one-minus-src-alpha",
                operation: "add",
              },
              alpha: {
                srcFactor: "one",
                dstFactor: "one-minus-src-alpha",
                operation: "add",
              },
            },
          }],
        },
        primitive: { topology: "triangle-list" },
      });
      const ribbonPipeline = device.createRenderPipeline({
        layout: "auto",
        vertex: { module: shader, entryPoint: "ribbon_vs_main" },
        fragment: {
          module: shader,
          entryPoint: "ribbon_fs_main",
          targets: [{
            format,
            blend: {
              color: { srcFactor: "one", dstFactor: "one", operation: "add" },
              alpha: {
                srcFactor: "one",
                dstFactor: "one-minus-src-alpha",
                operation: "add",
              },
            },
          }],
        },
        primitive: { topology: "triangle-list" },
      });
      const ribbonCompositePipeline = device.createRenderPipeline({
        layout: "auto",
        vertex: { module: shader, entryPoint: "vs_main" },
        fragment: {
          module: shader,
          entryPoint: "ribbon_composite_fs_main",
          targets: [{
            format,
            blend: {
              color: {
                srcFactor: "one",
                dstFactor: "one-minus-src-alpha",
                operation: "add",
              },
              alpha: {
                srcFactor: "one",
                dstFactor: "one-minus-src-alpha",
                operation: "add",
              },
            },
          }],
        },
        primitive: { topology: "triangle-list" },
      });
      const values = new Float32Array(displayedUniforms);
      const uniformBuffer = device.createBuffer({
        size: values.byteLength,
        usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
      });
      const bindGroup = device.createBindGroup({
        layout: pipeline.getBindGroupLayout(0),
        entries: [{ binding: 0, resource: { buffer: uniformBuffer } }],
      });
      const ribbonBindGroup = device.createBindGroup({
        layout: ribbonPipeline.getBindGroupLayout(0),
        entries: [{ binding: 0, resource: { buffer: uniformBuffer } }],
      });
      const ribbonSampler = device.createSampler({
        addressModeU: "clamp-to-edge",
        addressModeV: "clamp-to-edge",
        magFilter: "linear",
        minFilter: "linear",
      });
      let ribbonCompositeBindGroup = null;
      device.lost.then((info) => {
        stopWithError(new Error(\`WebGPU device lost: \${info.message || info.reason}\`));
      });
      device.addEventListener("uncapturederror", (event) => {
        event.preventDefault();
        stopWithError(new Error(\`WebGPU rendering error: \${event.error.message}\`));
      });

      function frame(now) {
        if (stopped) return;
        try {
          const dpr = Math.min(window.devicePixelRatio || 1, 2);
          const width = Math.max(1, Math.floor(canvas.clientWidth * dpr));
          const height = Math.max(1, Math.floor(canvas.clientHeight * dpr));
          if (canvas.width !== width || canvas.height !== height) {
            canvas.width = width;
            canvas.height = height;
            ribbonTarget?.destroy();
            ribbonTarget = null;
            ribbonCompositeBindGroup = null;
          }
          values.set(sampleTransition(now));
          const frameDelta = lastFrameAt === null
            ? 0
            : Math.min(0.1, Math.max(0, (now - lastFrameAt) / 1000));
          lastFrameAt = now;
          motionPhase += frameDelta * Math.max(values[3], 0);
          values[0] = width;
          values[1] = height;
          values[2] = motionPhase / Math.max(values[3], 0.001);
          device.queue.writeBuffer(uniformBuffer, 0, values);

          const isParticleRibbon = Math.round(values[15]) === ribbonStyleIndex;
          const encoder = device.createCommandEncoder();
          if (isParticleRibbon) {
            if (!ribbonTarget || !ribbonCompositeBindGroup) {
              ribbonTarget = device.createTexture({
                size: { width, height },
                format,
                usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.TEXTURE_BINDING,
              });
              ribbonCompositeBindGroup = device.createBindGroup({
                layout: ribbonCompositePipeline.getBindGroupLayout(0),
                entries: [
                  { binding: 0, resource: { buffer: uniformBuffer } },
                  { binding: 1, resource: ribbonTarget.createView() },
                  { binding: 2, resource: ribbonSampler },
                ],
              });
            }
            const particlePass = encoder.beginRenderPass({
              colorAttachments: [{
                view: ribbonTarget.createView(),
                clearValue: { r: 0, g: 0, b: 0, a: 0 },
                loadOp: "clear",
                storeOp: "store",
              }],
            });
            particlePass.setPipeline(ribbonPipeline);
            particlePass.setBindGroup(0, ribbonBindGroup);
            particlePass.draw(6, ribbonInstanceCount);
            particlePass.end();
          }
          const pass = encoder.beginRenderPass({
            colorAttachments: [{
              view: context.getCurrentTexture().createView(),
              clearValue: { r: 0, g: 0, b: 0, a: 0 },
              loadOp: "clear",
              storeOp: "store",
            }],
          });
          if (isParticleRibbon) {
            pass.setPipeline(ribbonCompositePipeline);
            pass.setBindGroup(0, ribbonCompositeBindGroup);
          } else {
            pass.setPipeline(pipeline);
            pass.setBindGroup(0, bindGroup);
          }
          pass.draw(3);
          pass.end();
          device.queue.submit([encoder.finish()]);
          animationFrame = requestAnimationFrame(frame);
        } catch (error) {
          stopWithError(error);
        }
      }

      animationFrame = requestAnimationFrame(frame);
    }

    window.addEventListener("pagehide", () => {
      stopped = true;
      cancelAnimationFrame(animationFrame);
      ribbonTarget?.destroy();
      device?.destroy();
    }, { once: true });
    start().catch((error) => {
      stopWithError(error);
    });
  <\/script>
</body>
</html>`}function hy(e,t){let n=py(e);return`import Foundation
import MetalKit
import QuartzCore
import SwiftUI

private let orbMetalSource = #"""
${kv}
"""#

private let orbIdleUniformSeed: [Float] = [
${fy(n.idle)}
]

private let orbThinkingUniformSeed: [Float] = [
${fy(n.thinking)}
]

private let orbActivationDuration: CFTimeInterval = ${e.activationDuration}
private let orbSettleDuration: CFTimeInterval = ${e.transitionDuration}
private let orbRibbonStyleIndex: Float = ${Pv.particleRibbon}
private let orbRibbonInstanceCount = ${Bv}

public enum LiquidOrbState: Sendable {
    case idle
    case thinking
}

private func orbUniformSeed(for state: LiquidOrbState) -> [Float] {
    switch state {
    case .idle: orbIdleUniformSeed
    case .thinking: orbThinkingUniformSeed
    }
}

private func orbSrgbToLinear(_ value: Float) -> Float {
    value <= 0.04045
        ? value / 12.92
        : Float(pow(Double((value + 0.055) / 1.055), 2.4))
}

private func orbLinearToSrgb(_ value: Float) -> Float {
    value <= 0.0031308
        ? value * 12.92
        : 1.055 * Float(pow(Double(value), 1.0 / 2.4)) - 0.055
}

private func orbMixSrgb(_ from: Float, _ to: Float, _ progress: Float) -> Float {
    orbLinearToSrgb(
        orbSrgbToLinear(from) + (orbSrgbToLinear(to) - orbSrgbToLinear(from)) * progress
    )
}

private enum LiquidOrbError: Error {
    case metalUnavailable
    case shaderFunctionMissing(String)
    case commandQueueUnavailable
}

private final class LiquidOrbRenderer: NSObject, MTKViewDelegate {
    private let commandQueue: MTLCommandQueue
    private let pipeline: MTLRenderPipelineState
    private let ribbonPipeline: MTLRenderPipelineState
    private let ribbonCompositePipeline: MTLRenderPipelineState
    private var ribbonTexture: MTLTexture?
    private var lastFrameAt = CACurrentMediaTime()
    private var motionPhase: CFTimeInterval = 0
    private let stateLock = NSLock()
    private var currentState: LiquidOrbState
    private var transitionTargetState: LiquidOrbState
    private var fromUniforms: [Float]
    private var targetUniforms: [Float]
    private var displayedUniforms: [Float]
    private var transitionStartedAt = CACurrentMediaTime()
    private var activeTransitionDuration: CFTimeInterval = 0

    init(view: MTKView, state: LiquidOrbState) throws {
        let initialUniforms = orbUniformSeed(for: state)
        currentState = state
        transitionTargetState = state
        fromUniforms = initialUniforms
        targetUniforms = initialUniforms
        displayedUniforms = initialUniforms

        guard let device = MTLCreateSystemDefaultDevice() else {
            throw LiquidOrbError.metalUnavailable
        }
        view.device = device
        view.colorPixelFormat = .bgra8Unorm
        view.framebufferOnly = true
        view.preferredFramesPerSecond = 60
        view.enableSetNeedsDisplay = false
        view.isPaused = false
        #if os(iOS)
        view.isOpaque = false
        #elseif os(macOS)
        view.layer?.isOpaque = false
        #endif
        view.clearColor = MTLClearColor(
            red: 0,
            green: 0,
            blue: 0,
            alpha: 0
        )

        let library = try device.makeLibrary(source: orbMetalSource, options: nil)
        guard let vertex = library.makeFunction(name: "vs_main") else {
            throw LiquidOrbError.shaderFunctionMissing("vs_main")
        }
        guard let fragment = library.makeFunction(name: "fs_main") else {
            throw LiquidOrbError.shaderFunctionMissing("fs_main")
        }
        let descriptor = MTLRenderPipelineDescriptor()
        descriptor.vertexFunction = vertex
        descriptor.fragmentFunction = fragment
        descriptor.colorAttachments[0].pixelFormat = view.colorPixelFormat
        descriptor.colorAttachments[0].isBlendingEnabled = true
        descriptor.colorAttachments[0].sourceRGBBlendFactor = .one
        descriptor.colorAttachments[0].destinationRGBBlendFactor = .oneMinusSourceAlpha
        descriptor.colorAttachments[0].sourceAlphaBlendFactor = .one
        descriptor.colorAttachments[0].destinationAlphaBlendFactor = .oneMinusSourceAlpha
        pipeline = try device.makeRenderPipelineState(descriptor: descriptor)
        guard let ribbonVertex = library.makeFunction(name: "ribbon_vs_main") else {
            throw LiquidOrbError.shaderFunctionMissing("ribbon_vs_main")
        }
        guard let ribbonFragment = library.makeFunction(name: "ribbon_fs_main") else {
            throw LiquidOrbError.shaderFunctionMissing("ribbon_fs_main")
        }
        let ribbonDescriptor = MTLRenderPipelineDescriptor()
        ribbonDescriptor.vertexFunction = ribbonVertex
        ribbonDescriptor.fragmentFunction = ribbonFragment
        ribbonDescriptor.colorAttachments[0].pixelFormat = view.colorPixelFormat
        ribbonDescriptor.colorAttachments[0].isBlendingEnabled = true
        ribbonDescriptor.colorAttachments[0].sourceRGBBlendFactor = .one
        ribbonDescriptor.colorAttachments[0].destinationRGBBlendFactor = .one
        ribbonDescriptor.colorAttachments[0].sourceAlphaBlendFactor = .one
        ribbonDescriptor.colorAttachments[0].destinationAlphaBlendFactor = .oneMinusSourceAlpha
        ribbonPipeline = try device.makeRenderPipelineState(descriptor: ribbonDescriptor)
        guard let ribbonCompositeFragment = library.makeFunction(
            name: "ribbon_composite_fs_main"
        ) else {
            throw LiquidOrbError.shaderFunctionMissing("ribbon_composite_fs_main")
        }
        let ribbonCompositeDescriptor = MTLRenderPipelineDescriptor()
        ribbonCompositeDescriptor.vertexFunction = vertex
        ribbonCompositeDescriptor.fragmentFunction = ribbonCompositeFragment
        ribbonCompositeDescriptor.colorAttachments[0].pixelFormat = view.colorPixelFormat
        ribbonCompositeDescriptor.colorAttachments[0].isBlendingEnabled = true
        ribbonCompositeDescriptor.colorAttachments[0].sourceRGBBlendFactor = .one
        ribbonCompositeDescriptor.colorAttachments[0].destinationRGBBlendFactor = .oneMinusSourceAlpha
        ribbonCompositeDescriptor.colorAttachments[0].sourceAlphaBlendFactor = .one
        ribbonCompositeDescriptor.colorAttachments[0].destinationAlphaBlendFactor = .oneMinusSourceAlpha
        ribbonCompositePipeline = try device.makeRenderPipelineState(
            descriptor: ribbonCompositeDescriptor
        )
        guard let queue = device.makeCommandQueue() else {
            throw LiquidOrbError.commandQueueUnavailable
        }
        commandQueue = queue
        super.init()
    }

    func setState(_ state: LiquidOrbState) {
        let now = CACurrentMediaTime()
        stateLock.lock()
        defer { stateLock.unlock() }
        guard state != currentState else { return }

        let nextUniforms = orbUniformSeed(for: state)
        fromUniforms = sampleTransition(at: now)
        targetUniforms = nextUniforms
        transitionTargetState = state
        transitionStartedAt = now
        activeTransitionDuration = state == .thinking
            ? orbActivationDuration
            : orbSettleDuration
        currentState = state
    }

    private func sampleTransition(at now: CFTimeInterval) -> [Float] {
        let rawProgress = activeTransitionDuration == 0
            ? 1
            : min(1, max(0, (now - transitionStartedAt) / activeTransitionDuration))
        let easedProgress = transitionTargetState == .thinking
            ? 1 - pow(1 - rawProgress, 3)
            : rawProgress * rawProgress * (3 - 2 * rawProgress)
        let progress = Float(easedProgress)

        for index in 3..<displayedUniforms.count {
            let isColorComponent = index >= 40
                && (index - 40) % 4 < 3
            displayedUniforms[index] = isColorComponent
                ? orbMixSrgb(fromUniforms[index], targetUniforms[index], progress)
                : fromUniforms[index] + (targetUniforms[index] - fromUniforms[index]) * progress
        }
        return displayedUniforms
    }

    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {
        ribbonTexture = nil
    }

    private func ensureRibbonTexture(for view: MTKView) -> MTLTexture? {
        let width = max(1, Int(view.drawableSize.width))
        let height = max(1, Int(view.drawableSize.height))
        if let ribbonTexture,
           ribbonTexture.width == width,
           ribbonTexture.height == height {
            return ribbonTexture
        }
        guard let device = view.device else { return nil }
        let descriptor = MTLTextureDescriptor.texture2DDescriptor(
            pixelFormat: view.colorPixelFormat,
            width: width,
            height: height,
            mipmapped: false
        )
        descriptor.usage = [.renderTarget, .shaderRead]
        descriptor.storageMode = .private
        ribbonTexture = device.makeTexture(descriptor: descriptor)
        return ribbonTexture
    }

    func draw(in view: MTKView) {
        guard
            view.drawableSize.width > 0,
            view.drawableSize.height > 0,
            let descriptor = view.currentRenderPassDescriptor,
            let drawable = view.currentDrawable,
            let commandBuffer = commandQueue.makeCommandBuffer()
        else { return }

        let now = CACurrentMediaTime()
        stateLock.lock()
        var uniforms = sampleTransition(at: now)
        stateLock.unlock()
        let frameDelta = min(0.1, max(0, now - lastFrameAt))
        lastFrameAt = now
        motionPhase += frameDelta * CFTimeInterval(max(uniforms[3], 0))
        uniforms[0] = Float(view.drawableSize.width)
        uniforms[1] = Float(view.drawableSize.height)
        uniforms[2] = Float(motionPhase / CFTimeInterval(max(uniforms[3], 0.001)))
        let isParticleRibbon = round(uniforms[15]) == orbRibbonStyleIndex
        if isParticleRibbon {
            guard let ribbonTexture = ensureRibbonTexture(for: view) else { return }
            let ribbonPass = MTLRenderPassDescriptor()
            ribbonPass.colorAttachments[0].texture = ribbonTexture
            ribbonPass.colorAttachments[0].loadAction = .clear
            ribbonPass.colorAttachments[0].storeAction = .store
            ribbonPass.colorAttachments[0].clearColor = MTLClearColor(
                red: 0, green: 0, blue: 0, alpha: 0
            )
            guard let ribbonEncoder = commandBuffer.makeRenderCommandEncoder(
                descriptor: ribbonPass
            ) else { return }
            ribbonEncoder.setRenderPipelineState(ribbonPipeline)
            uniforms.withUnsafeBytes { bytes in
                ribbonEncoder.setVertexBytes(bytes.baseAddress!, length: bytes.count, index: 0)
                ribbonEncoder.setFragmentBytes(bytes.baseAddress!, length: bytes.count, index: 0)
            }
            ribbonEncoder.drawPrimitives(
                type: .triangle,
                vertexStart: 0,
                vertexCount: 6,
                instanceCount: orbRibbonInstanceCount
            )
            ribbonEncoder.endEncoding()
        }
        guard let encoder = commandBuffer.makeRenderCommandEncoder(descriptor: descriptor) else {
            return
        }
        encoder.setRenderPipelineState(isParticleRibbon ? ribbonCompositePipeline : pipeline)
        uniforms.withUnsafeBytes { bytes in
            encoder.setFragmentBytes(bytes.baseAddress!, length: bytes.count, index: 0)
        }
        if isParticleRibbon {
            encoder.setFragmentTexture(ribbonTexture, index: 0)
        }
        encoder.drawPrimitives(type: .triangle, vertexStart: 0, vertexCount: 3)
        encoder.endEncoding()
        commandBuffer.present(drawable)
        commandBuffer.commit()
    }
}

private final class LiquidOrbCoordinator {
    private var renderer: LiquidOrbRenderer?

    func makeView(state: LiquidOrbState) -> MTKView {
        let view = MTKView(frame: .zero, device: nil)
        do {
            let renderer = try LiquidOrbRenderer(view: view, state: state)
            self.renderer = renderer
            view.delegate = renderer
            return view
        } catch {
            preconditionFailure("Liquid Orb Metal initialization failed: \\(error)")
        }
    }

    func setState(_ state: LiquidOrbState) {
        renderer?.setState(state)
    }
}

#if os(iOS)
private struct LiquidOrbSurface: UIViewRepresentable {
    let state: LiquidOrbState

    func makeCoordinator() -> LiquidOrbCoordinator { LiquidOrbCoordinator() }
    func makeUIView(context: Context) -> MTKView { context.coordinator.makeView(state: state) }
    func updateUIView(_ view: MTKView, context: Context) { context.coordinator.setState(state) }
}
#elseif os(macOS)
private struct LiquidOrbSurface: NSViewRepresentable {
    let state: LiquidOrbState

    func makeCoordinator() -> LiquidOrbCoordinator { LiquidOrbCoordinator() }
    func makeNSView(context: Context) -> MTKView { context.coordinator.makeView(state: state) }
    func updateNSView(_ view: MTKView, context: Context) { context.coordinator.setState(state) }
}
#endif

public struct LiquidOrbView: View {
    private let state: LiquidOrbState

    public init(state: LiquidOrbState = .${t}) {
        self.state = state
    }

    public var body: some View {
        LiquidOrbSurface(state: state)
    }
}`}var gy=[{label:`中`,value:`zh`},{label:`EN`,value:`en`}],_y={zh:{siri:`Siri 波澜`,voiceWave:`声纹薄膜`,spectrum:`彩色声场`,aurora:`极光帷幕`,frost:`冰霜流体`,plasma:`神经电浆`,chrome:`液态铬`,opal:`虹彩欧泊`,blueDrop:`蓝晶液滴`,violetEmber:`紫焰流核`,refractiveBlob:`折射软体`,particleRibbon:`量子丝带`,chromaticMetal:`色差液态金属`},en:{siri:`Siri Wave`,voiceWave:`Voice Membrane`,spectrum:`Prismatic Field`,aurora:`Aurora Veil`,frost:`Frost Flow`,plasma:`Neural Plasma`,chrome:`Liquid Chrome`,opal:`Iridescent Opal`,blueDrop:`Crystal Drop`,violetEmber:`Violet Ember`,refractiveBlob:`Refractive Gel`,particleRibbon:`Particle Ribbons`,chromaticMetal:`Chromatic Metal`}},vy={zh:{speed:`速度`,radius:`半径`,contourDeform:`轮廓形变`,zoom:`缩放`,warp:`扭曲`,ridgeAmt:`脊线`,sharp:`锐度`,bandDensity:`重复次数`,metalDepth:`金属深度`,metalRoughness:`表面粗糙度`,chromaticShift:`RGB 分离`,metalScale:`图案缩放`,metalStretch:`纵横拉伸`,metalAngle:`流带角度`,metalOffset:`图案偏移`,metalPhase:`循环相位`,metalEvolution:`演化幅度`,particleDensity:`粒子密度`,ribbonCount:`丝带层数`,ribbonWidth:`丝带宽度`,ribbonTwist:`扭转强度`,ribbonFold:`折叠幅度`,ribbonBreath:`呼吸幅度`,particleSize:`粒子尺寸`,particleBloom:`粒子辉光`,shade:`明暗`,exposure:`曝光`,sheen:`边缘高光`,gloss:`色散`,glassOpacity:`折射强度`,shellMidAlpha:`折射宽度`,shellEdgeAlpha:`边缘强度`,edgeSoftness:`边缘柔化`,edgeGlow:`外发光强度`},en:{speed:`Speed`,radius:`Radius`,contourDeform:`Contour Motion`,zoom:`Flow Scale`,warp:`Flow Distortion`,ridgeAmt:`Ridge Detail`,sharp:`Sharpness`,bandDensity:`Band Count`,metalDepth:`Metallic Depth`,metalRoughness:`Roughness`,chromaticShift:`RGB Split`,metalScale:`Pattern Scale`,metalStretch:`Aspect Stretch`,metalAngle:`Band Angle`,metalOffset:`Pattern Offset`,metalPhase:`Loop Phase`,metalEvolution:`Flow Evolution`,particleDensity:`Particle Density`,ribbonCount:`Ribbon Layers`,ribbonWidth:`Ribbon Width`,ribbonTwist:`Twist`,ribbonFold:`Folding`,ribbonBreath:`Breathing`,particleSize:`Particle Size`,particleBloom:`Particle Bloom`,shade:`Shading`,exposure:`Exposure`,sheen:`Rim Highlight`,gloss:`Dispersion`,glassOpacity:`Refraction Strength`,shellMidAlpha:`Refraction Width`,shellEdgeAlpha:`Edge Intensity`,edgeSoftness:`Edge Softness`,edgeGlow:`Outer Glow`}},yy={zh:{colorA:`颜色 A`,colorB:`颜色 B`,colorC:`颜色 C`,colorD:`颜色 D`,highlightColor:`提亮色`,shellInner:`折射底色`,shellMid:`冷色散`,shellEdge:`暖色散`,sheenColor:`主高光色`,specColor:`辅高光色`,canvasColor:`背景颜色`,glowColor:`外发光颜色`},en:{colorA:`Color A`,colorB:`Color B`,colorC:`Color C`,colorD:`Color D`,highlightColor:`Highlight Tint`,shellInner:`Refraction Base`,shellMid:`Cool Dispersion`,shellEdge:`Warm Dispersion`,sheenColor:`Key Highlight`,specColor:`Fill Highlight`,canvasColor:`Background`,glowColor:`Glow Color`}},by={zh:{documentTitle:`液态玻璃球编辑器`,presets:`效果预设`,animatedPresets:`动态预设`,orbControls:`球体参数`,collapsePresets:`收起预设面板`,expandPresets:`展开预设面板`,collapseControls:`收起参数面板`,expandControls:`展开参数面板`,resetControls:`重置全部参数`,previewMode:`预览模式`,switchPreviewMode:`切换预览模式`,orbMode:`球体`,sceneMode:`场景`,switchLanguage:`切换界面语言`,orbPreview:`液态玻璃球预览`,scenePreview:`实际场景预览`,staticOrbPreview:`液态玻璃球静态预览`,animatedOrbPreview:`动态液态玻璃球`,loadingOrb:`正在加载球体`,renderFallback:`WebGPU 不可用，当前显示静态预览`,renderErrorTitle:`WebGPU 渲染失败`,sceneText:e=>`场景文字：${e}`,copyCode:`复制代码`,viewSource:`在 GitHub 查看源码`,sceneSection:`场景预览`,displayText:`显示文字`,sceneTextLimit:`最多 20 个字符`,stateSection:`AI 状态`,orbState:`当前状态`,switchOrbState:`切换 AI 球状态`,idleState:`空闲`,thinkingState:`思考中`,activationDuration:`启动时长`,transitionDuration:`回落时长`,collapseSection:e=>`收起${e}`,expandSection:e=>`展开${e}`,editValue:e=>`编辑${e}数值`,selectColor:e=>`选择${e}`,hexValue:e=>`${e}十六进制值`,hexColor:`十六进制颜色`,colorSurface:`颜色饱和度和亮度`,colorChannel:`通道`,cssColorValue:`CSS 颜色值`,hue:`色相`,motionSection:`动态`,colorsSection:`颜色`,shapeSection:`形状动画`,glassSection:`玻璃罩`,enableGlass:`开启玻璃罩`,edgeSection:`边缘与外发光`,copyFailed:`复制失败`,copied:`已复制`,close:`关闭`,webCode:`Web 代码`,swiftCode:`SwiftUI 代码`},en:{documentTitle:`Liquid Orb Editor`,presets:`Presets`,animatedPresets:`Animated presets`,orbControls:`Orb Controls`,collapsePresets:`Collapse presets`,expandPresets:`Expand presets`,collapseControls:`Collapse controls`,expandControls:`Expand controls`,resetControls:`Reset all controls`,previewMode:`Preview`,switchPreviewMode:`Switch preview mode`,orbMode:`Orb`,sceneMode:`Scene`,switchLanguage:`Switch interface language`,orbPreview:`Liquid glass orb preview`,scenePreview:`In-context preview`,staticOrbPreview:`Static liquid glass orb preview`,animatedOrbPreview:`Animated liquid glass orb`,loadingOrb:`Loading orb`,renderFallback:`WebGPU is unavailable. Showing the fallback preview.`,renderErrorTitle:`WebGPU rendering failed`,sceneText:e=>`Scene text: ${e}`,copyCode:`Copy Code`,viewSource:`View source on GitHub`,sceneSection:`Scene Preview`,displayText:`Display Text`,sceneTextLimit:`Up to 20 characters`,stateSection:`AI State`,orbState:`Current State`,switchOrbState:`Switch AI orb state`,idleState:`Idle`,thinkingState:`Thinking`,activationDuration:`Activation Duration`,transitionDuration:`Settle Duration`,collapseSection:e=>`Collapse ${e}`,expandSection:e=>`Expand ${e}`,editValue:e=>`Edit ${e} value`,selectColor:e=>`Choose ${e}`,hexValue:e=>`${e} hex value`,hexColor:`Hex color`,colorSurface:`Color saturation and brightness`,colorChannel:`channel`,cssColorValue:`CSS color value`,hue:`Hue`,motionSection:`Motion`,colorsSection:`Color`,shapeSection:`Shape Motion`,glassSection:`Glass Shell`,enableGlass:`Enable Glass Shell`,edgeSection:`Edge & Glow`,copyFailed:`Copy Failed`,copied:`Copied`,close:`Close`,webCode:`Web code`,swiftCode:`SwiftUI code`}};function xy({canvas:e,getTarget:t,onError:n,onReady:r}){let i=!1,a=0,o=null,s=null,c=!1,l=!1,u=null,d=0;function f(e){i||l||(l=!0,cancelAnimationFrame(a),s?.destroy(),o?.destroy(),n(e))}async function p(){if(!navigator.gpu)throw Error(`当前浏览器不支持 WebGPU`);let n=await navigator.gpu.requestAdapter();if(!n)throw Error(`未找到可用的 WebGPU 适配器`);if(o=await n.requestDevice(),i){o.destroy();return}let p=e.getContext(`webgpu`);if(!p)throw Error(`无法创建 WebGPU 画布上下文`);let m=p,h=navigator.gpu.getPreferredCanvasFormat();m.configure({device:o,format:h,alphaMode:`premultiplied`});let g=o.createShaderModule({label:`orb-glass-liquid`,code:dy}),_=(await g.getCompilationInfo()).messages.filter(e=>e.type===`error`);if(_.length>0)throw Error(_.map(e=>`${e.lineNum}:${e.linePos} ${e.message}`).join(`
`));let v=o.createRenderPipeline({label:`orb-glass-liquid-pipeline`,layout:`auto`,vertex:{module:g,entryPoint:`vs_main`},fragment:{module:g,entryPoint:`fs_main`,targets:[{format:h,blend:{color:{srcFactor:`one`,dstFactor:`one-minus-src-alpha`,operation:`add`},alpha:{srcFactor:`one`,dstFactor:`one-minus-src-alpha`,operation:`add`}}}]},primitive:{topology:`triangle-list`}}),y=o.createRenderPipeline({label:`particle-ribbon-pipeline`,layout:`auto`,vertex:{module:g,entryPoint:`ribbon_vs_main`},fragment:{module:g,entryPoint:`ribbon_fs_main`,targets:[{format:h,blend:{color:{srcFactor:`one`,dstFactor:`one`,operation:`add`},alpha:{srcFactor:`one`,dstFactor:`one-minus-src-alpha`,operation:`add`}}}]},primitive:{topology:`triangle-list`}}),b=o.createRenderPipeline({label:`particle-ribbon-glass-composite-pipeline`,layout:`auto`,vertex:{module:g,entryPoint:`vs_main`},fragment:{module:g,entryPoint:`ribbon_composite_fs_main`,targets:[{format:h,blend:{color:{srcFactor:`one`,dstFactor:`one-minus-src-alpha`,operation:`add`},alpha:{srcFactor:`one`,dstFactor:`one-minus-src-alpha`,operation:`add`}}}]},primitive:{topology:`triangle-list`}}),x=new Float32Array(136),S=o.createBuffer({size:x.byteLength,usage:GPUBufferUsage.UNIFORM|GPUBufferUsage.COPY_DST}),C=o.createBindGroup({layout:v.getBindGroupLayout(0),entries:[{binding:0,resource:{buffer:S}}]}),w=o.createBindGroup({layout:y.getBindGroupLayout(0),entries:[{binding:0,resource:{buffer:S}}]}),T=o.createSampler({addressModeU:`clamp-to-edge`,addressModeV:`clamp-to-edge`,magFilter:`linear`,minFilter:`linear`}),E=null,D=uy(t());o.lost.then(e=>{f(Error(`WebGPU 设备已断开：${e.message||e.reason}`))}),o.addEventListener(`uncapturederror`,e=>{e.preventDefault(),f(Error(`WebGPU 渲染错误：${e.error.message}`))});function O(){let t=Math.min(window.devicePixelRatio||1,2),n=Math.max(1,Math.floor(e.clientWidth*t)),r=Math.max(1,Math.floor(e.clientHeight*t));(e.width!==n||e.height!==r)&&(e.width=n,e.height=r,s?.destroy(),s=null,E=null)}function k(){s&&E||(s=o.createTexture({label:`particle-ribbon-offscreen-texture`,size:{width:e.width,height:e.height},format:h,usage:GPUTextureUsage.RENDER_ATTACHMENT|GPUTextureUsage.TEXTURE_BINDING}),E=o.createBindGroup({layout:b.getBindGroupLayout(0),entries:[{binding:0,resource:{buffer:S}},{binding:1,resource:s.createView()},{binding:2,resource:T}]}))}function A(n){if(!(i||l||!o))try{O();let i=D.sample(t(),n),l=u===null?0:Math.min(.1,Math.max(0,(n-u)/1e3));u=n,d+=l*Math.max(i.speed,0);let f=d/Math.max(i.speed,.001);Rv(x,e.width,e.height,f,i),o.queue.writeBuffer(S,0,x);let p=Pv[i.style]===Pv.particleRibbon,h=o.createCommandEncoder();if(p){k();let e=h.beginRenderPass({colorAttachments:[{view:s.createView(),clearValue:{r:0,g:0,b:0,a:0},loadOp:`clear`,storeOp:`store`}]});e.setPipeline(y),e.setBindGroup(0,w),e.draw(6,Bv,0,0),e.end()}let g=h.beginRenderPass({colorAttachments:[{view:m.getCurrentTexture().createView(),clearValue:{r:0,g:0,b:0,a:0},loadOp:`clear`,storeOp:`store`}]});p?(g.setPipeline(b),g.setBindGroup(0,E)):(g.setPipeline(v),g.setBindGroup(0,C)),g.draw(3,1,0,0),g.end(),o.queue.submit([h.finish()]),c||(c=!0,r()),a=requestAnimationFrame(A)}catch(e){f(e instanceof Error?e:Error(String(e)))}}a=requestAnimationFrame(A)}return p().catch(e=>{f(e instanceof Error?e:Error(String(e)))}),()=>{i=!0,cancelAnimationFrame(a),s?.destroy(),o?.destroy()}}var Sy=`modulepreload`,Cy=function(e,t){return new URL(e,t).href},wy={},Ty=function(e,t,n){let r=Promise.resolve();if(t&&t.length>0){let e=document.getElementsByTagName(`link`),i=document.querySelector(`meta[property=csp-nonce]`),a=i?.nonce||i?.getAttribute(`nonce`);function o(e){return Promise.all(e.map(e=>Promise.resolve(e).then(e=>({status:`fulfilled`,value:e}),e=>({status:`rejected`,reason:e}))))}function s(e){return import.meta.resolve?import.meta.resolve(e):new URL(e,import.meta.url).href}r=o(t.map(t=>{if(t=Cy(t,n),t=s(t),t in wy)return;wy[t]=!0;let r=t.endsWith(`.css`);for(let n=e.length-1;n>=0;n--){let i=e[n];if(i.href===t&&(!r||i.rel===`stylesheet`))return}let i=document.createElement(`link`);if(i.rel=r?`stylesheet`:Sy,r||(i.as=`script`),i.crossOrigin=``,i.href=t,a&&i.setAttribute(`nonce`,a),document.head.appendChild(i),r)return new Promise((e,n)=>{i.addEventListener(`load`,e),i.addEventListener(`error`,()=>n(Error(`Unable to preload CSS for ${t}`)))})}))}function i(e){let t=new Event(`vite:preloadError`,{cancelable:!0});if(t.payload=e,window.dispatchEvent(t),!t.defaultPrevented)throw e}return r.then(t=>{for(let e of t||[])e.status===`rejected`&&i(e.reason);return e().catch(i)})},Ey=_.lazy(async()=>({default:(await Ty(()=>import(`./color-control-CLrO6iRz.js`),[],import.meta.url)).ColorControl})),Dy={siri:Tv,voiceWave:Ov,spectrum:Ev,aurora:gv,frost:bv,plasma:Cv,chrome:vv,opal:xv,blueDrop:_v,violetEmber:Dv,refractiveBlob:wv,particleRibbon:Sv,chromaticMetal:yv},Oy=new Set([`particleRibbon`,`blueDrop`,`violetEmber`,`refractiveBlob`,`chromaticMetal`]),ky=`Thinking...`,Ay=20,jy=500,My=`liquid-orb-editor-locale`,Ny={min:.05,max:.8,step:.01},Py={min:.1,max:2,step:.05},Fy=[`siri`,`voiceWave`,`spectrum`,`aurora`,`frost`,`plasma`,`blueDrop`,`violetEmber`,`refractiveBlob`],Iy=[`frost`,`plasma`,`chrome`,`blueDrop`,`violetEmber`,`refractiveBlob`],Ly=Nv.filter(e=>e!==`chromaticMetal`&&e!==`particleRibbon`),Ry=[`chromaticMetal`],zy=[`particleRibbon`],By=[{key:`speed`,min:0,max:3,step:.01},{key:`radius`,...Av,step:.01},{key:`contourDeform`,min:0,max:1,step:.01,enabledStyles:Ly},{key:`zoom`,min:.05,max:1,step:.01,enabledStyles:Ly},{key:`warp`,min:0,max:6,step:.05,enabledStyles:Ly},{key:`ridgeAmt`,min:0,max:1,step:.01,enabledStyles:Fy},{key:`sharp`,min:.5,max:6,step:.05,enabledStyles:Iy},{key:`bandDensity`,min:1,max:6,step:.1,enabledStyles:Ry},{key:`metalDepth`,min:0,max:1,step:.01,enabledStyles:Ry},{key:`metalRoughness`,min:0,max:1,step:.01,enabledStyles:Ry},{key:`chromaticShift`,min:0,max:1,step:.01,enabledStyles:Ry},{key:`metalScale`,min:.2,max:2,step:.01,enabledStyles:Ry},{key:`metalStretch`,min:0,max:1,step:.01,enabledStyles:Ry},{key:`metalAngle`,min:-180,max:180,step:1,enabledStyles:Ry},{key:`metalOffset`,min:-1,max:1,step:.01,enabledStyles:Ry},{key:`metalPhase`,min:0,max:1,step:.01,enabledStyles:Ry},{key:`metalEvolution`,min:0,max:2,step:.02,enabledStyles:Ry},{key:`particleDensity`,min:.2,max:1,step:.01,enabledStyles:zy},{key:`ribbonCount`,min:2,max:6,step:1,enabledStyles:zy},{key:`ribbonWidth`,min:.1,max:.8,step:.01,enabledStyles:zy},{key:`ribbonTwist`,min:.1,max:3,step:.01,enabledStyles:zy},{key:`ribbonFold`,min:0,max:1.2,step:.01,enabledStyles:zy},{key:`ribbonBreath`,min:0,max:.8,step:.01,enabledStyles:zy},{key:`particleSize`,min:.6,max:2.5,step:.01,enabledStyles:zy},{key:`particleBloom`,min:0,max:2,step:.01,enabledStyles:zy},{key:`shade`,min:0,max:1.5,step:.01},{key:`exposure`,min:.2,max:3,step:.02},{key:`sheen`,min:0,max:2,step:.02},{key:`gloss`,min:0,max:2,step:.02},{key:`glassOpacity`,min:0,max:1,step:.01},{key:`shellMidAlpha`,min:0,max:1,step:.01},{key:`shellEdgeAlpha`,min:0,max:1,step:.01},{key:`edgeSoftness`,min:.005,max:.15,step:.005},{key:`edgeGlow`,min:0,max:1,step:.01}],Vy=new Map(By.map(e=>[e.key,e])),Hy=[`colorA`,`colorB`,`colorC`,`colorD`,`highlightColor`,`shellInner`,`shellMid`,`shellEdge`,`sheenColor`,`specColor`,`canvasColor`,`glowColor`];function Uy(e,t,n){return Math.min(n,Math.max(t,e))}function Wy(e){return/^#[0-9a-f]{6}$/i.test(e)?e.toUpperCase():null}function Gy(e){return Array.from(e).slice(0,Ay).join(``)}function Ky(){try{let e=window.localStorage.getItem(My);if(e===`zh`||e===`en`)return e}catch(e){console.warn(`Unable to read the saved interface language.`,e)}return navigator.language.toLowerCase().startsWith(`zh`)?`zh`:`en`}function qy(){return new URLSearchParams(window.location.hash.slice(1)).get(`preview`)===`scene`?`scene`:`orb`}function Jy(){let e=new URLSearchParams(window.location.hash.slice(1)).get(`text`);return e===null?ky:Gy(e)}function Yy(e,t){return e===`thinking`?t:`idle${t.charAt(0).toUpperCase()}${t.slice(1)}`}function Xy(){let e=new URLSearchParams(window.location.hash.slice(1)),t=e.get(`style`),n=t&&Nv.includes(t)?t:Fv.style,r={style:n,...Mv[n]},i=e.get(`glass`);i===`1`&&(r.glassEnabled=!0),i===`0`&&(r.glassEnabled=!1);for(let t of By){let n=e.get(t.key);if(n===null)continue;let i=Number(n);Number.isFinite(i)&&(r[t.key]=Uy(i,t.min,t.max))}for(let t of Hy){let n=e.get(t);if(n===null)continue;let i=Wy(n);i&&(r[t]=i)}let a=e.get(`transition`),o=a===null?null:Number(a),s=o!==null&&Number.isFinite(o)?Uy(o,Py.min,Py.max):qv,c=e.get(`activation`),l=c===null?null:Number(c),u=$v(r,s,l!==null&&Number.isFinite(l)?Uy(l,Ny.min,Ny.max):Kv);for(let t of Wv){let n=e.get(Yy(`idle`,t));if(n!==null){if(typeof u.profiles.idle[t]==`number`){let e=Vy.get(t),r=Number(n);e&&Number.isFinite(r)&&(u=ny(u,`idle`,t,Uy(r,e.min,e.max)))}else{let e=Wy(n);e&&(u=ny(u,`idle`,t,e))}}}let d=e.get(`state`),f=d&&Vv.includes(d)?d:Gv;return{configuration:u,activeState:f}}function Zy(e,t,n){let{configuration:r,activeState:i}=e,a=ty(r,`thinking`),o=new URLSearchParams;o.set(`effect`,`orb-glass-liquid`),o.set(`style`,a.style),o.set(`glass`,a.glassEnabled?`1`:`0`),o.set(`state`,i),o.set(`activation`,String(r.activationDuration)),o.set(`transition`,String(r.transitionDuration)),o.set(`preview`,t),o.set(`text`,n);for(let e of By)o.set(e.key,String(a[e.key])),Xv(e.key)&&o.set(Yy(`idle`,e.key),String(r.profiles.idle[e.key]));for(let e of Hy)o.set(e,a[e]),Xv(e)&&o.set(Yy(`idle`,e),r.profiles.idle[e]);window.history.replaceState(null,``,`#${o.toString()}`)}function Qy(){let[e,t]=_.useState({state:!1,motion:!1,colors:!0,shape:!0,glass:!1,edge:!1,scene:!1});return{isCollapsed:t=>e[t]??!1,onCollapsedChange:e=>n=>{t(t=>({...t,[e]:n}))}}}function $y(){let[e,t]=_.useState(()=>window.matchMedia(`(max-width: 900px)`).matches);return _.useEffect(()=>{let e=window.matchMedia(`(max-width: 900px)`),n=()=>t(e.matches);return e.addEventListener(`change`,n),()=>e.removeEventListener(`change`,n)},[]),e}function eb(){let[e,t]=_.useState(Ky),[n,r]=_.useState(Xy),[i,a]=_.useState(`loading`),[o,s]=_.useState(``),[c,l]=_.useState(!1),[u,d]=_.useState(!1),[f,p]=_.useState(1),[m,h]=_.useState(qy),[g,v]=_.useState(Jy),[y,b]=_.useState(!1),[x,S]=_.useState(`web`),[C,w]=_.useState(null),[T,E]=_.useState(null),D=_.useRef(null),O=_.useRef(null),k=_.useRef(null),A=ty(n.configuration,n.activeState),P=_.useMemo(()=>ty(ey(A.style),n.activeState),[n.activeState,A.style]),F=_.useRef({state:n.activeState,params:A,activationDuration:n.configuration.activationDuration,transitionDuration:n.configuration.transitionDuration}),I=Qy(),L=$y(),R=by[e],z=_.useMemo(()=>[{label:R.orbMode,value:`orb`},{label:R.sceneMode,value:`scene`}],[R.orbMode,R.sceneMode]),B=_.useMemo(()=>[{label:R.idleState,value:`idle`},{label:R.thinkingState,value:`thinking`}],[R.idleState,R.thinkingState]),V=_.useMemo(()=>T?my(T.configuration,T.activeState):``,[T]),H=_.useMemo(()=>T?hy(T.configuration,T.activeState):``,[T]);F.current={state:n.activeState,params:A,activationDuration:n.configuration.activationDuration,transitionDuration:n.configuration.transitionDuration},_.useEffect(()=>{document.documentElement.lang=e===`zh`?`zh-CN`:`en`,document.title=by[e].documentTitle;try{window.localStorage.setItem(My,e)}catch(e){console.warn(`Unable to save the interface language.`,e)}},[e]),_.useEffect(()=>{let e=window.setTimeout(()=>{Zy(n,m,g)},jy);return()=>window.clearTimeout(e)},[n,m,g]),_.useEffect(()=>{let e=()=>{r(Xy()),h(qy()),v(Jy()),p(1)};return window.addEventListener(`hashchange`,e),()=>window.removeEventListener(`hashchange`,e)},[]),_.useEffect(()=>{document.documentElement.style.setProperty(`--orb-canvas-color`,A.canvasColor)},[A.canvasColor]),_.useEffect(()=>{let e=D.current;if(e)return xy({canvas:e,getTarget:()=>F.current,onError:e=>{s(e.message),a(`error`)},onReady:()=>a(e=>e===`ready`?e:`ready`)})},[]),_.useEffect(()=>{let e=O.current;if(!e)return;let t=t=>{if(t.target instanceof Element&&t.target.closest(`[data-stage-controls]`))return;t.preventDefault();let n=t.deltaMode===WheelEvent.DOM_DELTA_LINE?16:t.deltaMode===WheelEvent.DOM_DELTA_PAGE?e.clientHeight:1,r=Uy(-t.deltaY*n*.001,-.1,.1);p(e=>Math.round(Uy(e+r,.6,1.6)*100)/100)};return e.addEventListener(`wheel`,t,{passive:!1}),()=>e.removeEventListener(`wheel`,t)},[]);let U=_.useCallback((e,t)=>{r(n=>({...n,configuration:ny(n.configuration,n.activeState,e,t)}))},[]),W=_.useCallback(e=>{r(t=>({activeState:t.activeState,configuration:{...ey(e),activationDuration:t.configuration.activationDuration,transitionDuration:t.configuration.transitionDuration}}))},[]),ee=_.useCallback(()=>{r({activeState:Gv,configuration:ey(Fv.style)}),v(ky),p(1)},[]),te=_.useCallback(e=>{(e===`orb`||e===`scene`)&&(h(e),p(1))},[]),G=_.useCallback(e=>{Vv.includes(e)&&r(t=>({...t,activeState:e}))},[]),ne=_.useCallback(e=>{r(t=>({...t,configuration:{...t.configuration,transitionDuration:e}}))},[]),re=_.useCallback(e=>{r(t=>({...t,configuration:{...t.configuration,activationDuration:e}}))},[]),ie=_.useCallback(()=>{E({activeState:n.activeState,configuration:{...n.configuration,shared:{...n.configuration.shared},profiles:{idle:{...n.configuration.profiles.idle},thinking:{...n.configuration.profiles.thinking}}}}),w(null),b(!0)},[n]),ae=_.useCallback(async()=>{let e=x===`web`?V:H;try{await navigator.clipboard.writeText(e),w(x)}catch{let t=k.current,n=document.activeElement instanceof HTMLElement?document.activeElement:null;if(!t){w(`error`);return}t.value=e,t.focus(),t.select();let r=document.execCommand(`copy`);n?.focus(),w(r?x:`error`)}},[x,H,V]);function oe(t){let n=Vy.get(t);if(!n)throw Error(`Missing slider configuration: ${t}`);return n.enabledStyles&&!n.enabledStyles.includes(A.style)?null:(0,Z.jsx)(o_,{baseValue:P[t],editValueLabel:R.editValue(vy[e][t]),max:n.max,min:n.min,name:vy[e][t],onValueChange:e=>U(t,e),showFill:!0,step:n.step,value:A[t]},t)}function se(t){let n=yy[e][t];return{ariaLabels:{colorChannel:R.colorChannel,colorSurface:R.colorSurface,cssColorValue:R.cssColorValue,hexColor:R.hexColor,hexValue:R.hexValue(n),hue:R.hue,selectColor:R.selectColor(n)},hex:A[t],name:n,onValueChange:({hex:e})=>U(t,e),showLabel:!0}}function ce(e){return(0,Z.jsx)(_.Suspense,{fallback:(0,Z.jsx)(`div`,{className:`color-control-loading`,"aria-hidden":`true`}),children:e})}return(0,Z.jsxs)(nd,{children:[(0,Z.jsxs)(`main`,{className:`orb-editor`,"data-preset-collapsed":String(!L&&c),"data-properties-collapsed":String(!L&&u),children:[(0,Z.jsx)(`aside`,{className:`preset-dock`,"aria-label":R.presets,children:(0,Z.jsx)(x_,{className:`preset-panel h-full max-h-none w-full rounded-lg`,collapsed:c,collapseDirection:`left`,collapseLabel:R.collapsePresets,collapsible:!L,expandLabel:R.expandPresets,onCollapsedChange:l,title:R.presets,children:(0,Z.jsx)(g_,{children:(0,Z.jsx)(`div`,{className:`preset-control`,children:(0,Z.jsx)(`div`,{className:`preset-grid`,role:`group`,"aria-label":R.animatedPresets,children:Nv.map(t=>(0,Z.jsxs)(gr,{"aria-pressed":A.style===t,className:`preset-button`,onClick:()=>W(t),type:`button`,variant:`outline`,children:[(0,Z.jsx)(`img`,{alt:``,"aria-hidden":`true`,className:`preset-preview${Oy.has(t)?` preset-preview--compact`:``}`,src:Dy[t]}),(0,Z.jsx)(`span`,{title:_y[e][t],children:_y[e][t]})]},t))})})})})}),(0,Z.jsxs)(`section`,{className:`orb-stage`,"aria-label":m===`scene`?R.scenePreview:R.orbPreview,"data-preview-mode":m,ref:O,style:{"--preview-scale":f},children:[(0,Z.jsx)(`div`,{className:`language-control`,"data-stage-controls":!0,children:(0,Z.jsx)(qg,{ariaLabel:R.switchLanguage,name:R.switchLanguage,onValueChange:e=>{(e===`zh`||e===`en`)&&t(e)},options:gy,value:e})}),(0,Z.jsx)(`div`,{className:`stage-mode-control`,"data-stage-controls":!0,children:(0,Z.jsx)(qg,{ariaLabel:R.switchPreviewMode,name:R.previewMode,onValueChange:te,options:z,value:m})}),(0,Z.jsxs)(`div`,{className:`preview-surface`,children:[(0,Z.jsxs)(`div`,{className:`orb-visual`,children:[i===`error`?(0,Z.jsx)(`img`,{className:`orb-poster`,src:hv,alt:R.staticOrbPreview}):null,(0,Z.jsx)(`canvas`,{"aria-label":R.animatedOrbPreview,className:`orb-canvas`,"data-ready":i===`ready`?`true`:void 0,ref:D}),i===`loading`?(0,Z.jsxs)(`div`,{className:`orb-status`,role:`status`,"aria-live":`polite`,children:[(0,Z.jsx)(`span`,{className:`orb-spinner`,"aria-hidden":`true`}),(0,Z.jsx)(`span`,{className:`sr-only`,children:R.loadingOrb})]}):null,i===`error`?(0,Z.jsx)(`p`,{className:`orb-error`,title:e===`zh`?o:R.renderErrorTitle,children:R.renderFallback}):null]}),m===`scene`?(0,Z.jsx)(`div`,{className:`scene-copy`,"aria-label":R.sceneText(g),children:(0,Z.jsx)(`span`,{className:`scene-copy-text`,children:g||`\xA0`})}):null]}),(0,Z.jsxs)(`div`,{className:`stage-toolbar`,"data-stage-controls":!0,children:[(0,Z.jsxs)(gr,{className:`code-trigger`,onClick:ie,size:`lg`,type:`button`,variant:`outline`,children:[(0,Z.jsx)(j,{"data-icon":`inline-start`}),R.copyCode]}),(0,Z.jsxs)(rd,{children:[(0,Z.jsx)(id,{render:(0,Z.jsx)(`a`,{"aria-label":R.viewSource,className:`${mr({size:`icon-lg`,variant:`outline`})} github-link`,href:`https://github.com/LerSent001/orb`,rel:`noopener noreferrer`,target:`_blank`}),children:(0,Z.jsx)(N,{"aria-hidden":`true`,weight:`fill`})}),(0,Z.jsx)(ad,{side:`top`,children:R.viewSource})]})]})]}),(0,Z.jsx)(`aside`,{className:`panel-dock`,"aria-label":R.orbControls,children:(0,Z.jsxs)(x_,{className:`orb-editor-panel h-full max-h-none w-full rounded-lg`,collapsed:u,collapseDirection:`right`,collapseLabel:R.collapseControls,collapsible:!L,expandLabel:R.expandControls,onCollapsedChange:d,onResetControls:ee,resetLabel:R.resetControls,title:R.orbControls,children:[m===`scene`?(0,Z.jsx)(g_,{collapsed:I.isCollapsed(`scene`),collapseLabel:R.collapseSection(R.sceneSection),collapsible:!0,expandLabel:R.expandSection(R.sceneSection),onCollapsedChange:I.onCollapsedChange(`scene`),title:R.sceneSection,children:(0,Z.jsxs)(`div`,{className:`scene-text-field`,children:[(0,Z.jsxs)(`div`,{className:`scene-text-label-row`,children:[(0,Z.jsx)(Ud,{htmlFor:`scene-text-input`,children:R.displayText}),(0,Z.jsxs)(`span`,{"aria-live":`polite`,className:`scene-text-count`,children:[Array.from(g).length,`/`,Ay]})]}),(0,Z.jsx)(vo,{"aria-describedby":`scene-text-limit`,id:`scene-text-input`,onChange:e=>v(Gy(e.target.value)),value:g}),(0,Z.jsx)(`span`,{className:`sr-only`,id:`scene-text-limit`,children:R.sceneTextLimit})]})}):null,(0,Z.jsxs)(g_,{collapsed:I.isCollapsed(`state`),collapseLabel:R.collapseSection(R.stateSection),collapsible:!0,expandLabel:R.expandSection(R.stateSection),onCollapsedChange:I.onCollapsedChange(`state`),title:R.stateSection,children:[(0,Z.jsx)(`div`,{className:`orb-state-control`,children:(0,Z.jsx)(qg,{ariaLabel:R.switchOrbState,name:R.orbState,onValueChange:G,options:B,value:n.activeState})}),(0,Z.jsx)(o_,{baseValue:Kv,editValueLabel:R.editValue(R.activationDuration),max:Ny.max,min:Ny.min,name:R.activationDuration,onValueChange:re,showFill:!0,step:Ny.step,unit:`s`,value:n.configuration.activationDuration}),(0,Z.jsx)(o_,{baseValue:qv,editValueLabel:R.editValue(R.transitionDuration),max:Py.max,min:Py.min,name:R.transitionDuration,onValueChange:ne,showFill:!0,step:Py.step,unit:`s`,value:n.configuration.transitionDuration})]}),(0,Z.jsx)(g_,{collapsed:I.isCollapsed(`motion`),collapseLabel:R.collapseSection(R.motionSection),collapsible:!0,expandLabel:R.expandSection(R.motionSection),onCollapsedChange:I.onCollapsedChange(`motion`),title:R.motionSection,children:oe(`speed`)}),(0,Z.jsxs)(g_,{collapsed:I.isCollapsed(`colors`),collapseLabel:R.collapseSection(R.colorsSection),collapsible:!0,expandLabel:R.expandSection(R.colorsSection),onCollapsedChange:I.onCollapsedChange(`colors`),title:R.colorsSection,children:[ce((0,Z.jsx)(Ey,{inputs:[se(`colorA`),se(`colorB`)]})),ce((0,Z.jsx)(Ey,{inputs:[se(`colorC`),se(`colorD`)]})),ce((0,Z.jsx)(Ey,{inputs:[se(`highlightColor`),se(`canvasColor`)]})),oe(`shade`),oe(`exposure`)]}),(0,Z.jsxs)(g_,{collapsed:I.isCollapsed(`shape`),collapseLabel:R.collapseSection(R.shapeSection),collapsible:!0,expandLabel:R.expandSection(R.shapeSection),onCollapsedChange:I.onCollapsedChange(`shape`),title:R.shapeSection,children:[oe(`radius`),oe(`contourDeform`),oe(`zoom`),oe(`warp`),oe(`ridgeAmt`),oe(`sharp`),oe(`metalDepth`),oe(`metalRoughness`),oe(`chromaticShift`),oe(`metalScale`),oe(`metalStretch`),oe(`metalAngle`),oe(`bandDensity`),oe(`metalOffset`),oe(`metalPhase`),oe(`metalEvolution`),oe(`particleDensity`),oe(`ribbonCount`),oe(`ribbonWidth`),oe(`ribbonTwist`),oe(`ribbonFold`),oe(`ribbonBreath`),oe(`particleSize`),oe(`particleBloom`)]}),(0,Z.jsxs)(g_,{collapsed:I.isCollapsed(`glass`),collapseLabel:R.collapseSection(R.glassSection),collapsible:!0,expandLabel:R.expandSection(R.glassSection),onCollapsedChange:I.onCollapsedChange(`glass`),title:R.glassSection,children:[(0,Z.jsx)(`div`,{className:`glass-switch`,children:(0,Z.jsx)(ef,{checked:A.glassEnabled,name:R.enableGlass,onCheckedChange:e=>U(`glassEnabled`,e)})}),A.glassEnabled?(0,Z.jsxs)(Z.Fragment,{children:[oe(`glassOpacity`),oe(`sheen`),oe(`gloss`),oe(`shellMidAlpha`),oe(`shellEdgeAlpha`),ce((0,Z.jsx)(Ey,{inputs:[se(`shellInner`),se(`shellMid`)]})),ce((0,Z.jsx)(Ey,{inputs:[se(`shellEdge`),se(`sheenColor`)]})),ce((0,Z.jsx)(Ey,{...se(`specColor`)}))]}):null]}),(0,Z.jsxs)(g_,{collapsed:I.isCollapsed(`edge`),collapseLabel:R.collapseSection(R.edgeSection),collapsible:!0,expandLabel:R.expandSection(R.edgeSection),onCollapsedChange:I.onCollapsedChange(`edge`),title:R.edgeSection,children:[oe(`edgeSoftness`),oe(`edgeGlow`),ce((0,Z.jsx)(Ey,{...se(`glowColor`)}))]})]})})]}),(0,Z.jsx)(K_,{onOpenChange:e=>{b(e),e||w(null)},open:y,children:(0,Z.jsxs)(Y_,{className:`code-sheet`,closeLabel:R.close,side:`bottom`,children:[(0,Z.jsx)(`textarea`,{"aria-hidden":`true`,className:`code-copy-buffer`,ref:k,tabIndex:-1}),(0,Z.jsx)(X_,{className:`code-sheet-header`,children:(0,Z.jsx)(Z_,{children:R.copyCode})}),(0,Z.jsxs)(uv,{className:`code-tabs`,onValueChange:e=>{(e===`web`||e===`swift`)&&(S(e),w(null))},value:x,children:[(0,Z.jsxs)(`div`,{className:`code-sheet-toolbar`,children:[(0,Z.jsxs)(fv,{variant:`control`,children:[(0,Z.jsx)(pv,{value:`web`,children:`Web`}),(0,Z.jsx)(pv,{value:`swift`,children:`SwiftUI`})]}),(0,Z.jsxs)(gr,{onClick:ae,type:`button`,variant:`outline`,children:[(0,Z.jsx)(M,{"data-icon":`inline-start`}),C===`error`?R.copyFailed:C===x?R.copied:R.copyCode]})]}),(0,Z.jsx)(mv,{className:`code-tab-content`,value:`web`,children:(0,Z.jsx)(`pre`,{className:`code-preview`,"aria-label":R.webCode,children:(0,Z.jsx)(`code`,{children:V})})}),(0,Z.jsx)(mv,{className:`code-tab-content`,value:`swift`,children:(0,Z.jsx)(`pre`,{className:`code-preview`,"aria-label":R.swiftCode,children:(0,Z.jsx)(`code`,{children:H})})})]})]})})]})}var tb=document.querySelector(`#root`);if(!tb)throw Error(`找不到应用挂载节点`);(0,gt.createRoot)(tb).render((0,Z.jsx)(_.StrictMode,{children:(0,Z.jsx)(eb,{})}));export{c as C,u as S,Ad as _,Eg as a,Xn as b,ch as c,fm as d,mm as f,Ud as g,nf as h,vg as i,uh as l,gm as m,gg as n,bg as o,vm as p,Sg as r,yg as s,a_ as t,lh as u,cd as v,X as x,vo as y};