"use client";

import { useState, useEffect } from "react";
import * as Dialog from "@radix-ui/react-dialog";
import { MoreHorizontal, Plus, X, RefreshCw } from "lucide-react";

export default function TableWithDialog() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  
  // New user form state
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [location, setLocation] = useState("");
  const [status, setStatus] = useState("Active");
  const [balance, setBalance] = useState("0");
  const [avatar, setAvatar] = useState("");
  const [showAvatars, setShowAvatars] = useState(false);
  const presetAvatars = Array.from({ length: 30 }, (_, i) => `/static/avatars/avatar_${String(i + 1).padStart(2, "0")}.svg`);
  const [saving, setSaving] = useState(false);

  const fetchUsers = async () => {
      setLoading(true);
      try {
          const token = localStorage.getItem("dev_master_key") || "";
          const res = await fetch("/api/dev/users", { headers: { "x-master-key": token } });
          if (res.ok) {
              const data = await res.json();
              setUsers(data.users || []);
          }
      } catch (e) {}
      setLoading(false);
  };

  useEffect(() => {
      fetchUsers();
  }, []);

  const handleCreateUser = async (e: React.FormEvent) => {
      e.preventDefault();
      setSaving(true);
      try {
          const token = localStorage.getItem("dev_master_key") || "";
          const res = await fetch("/api/dev/users", {
              method: "POST",
              headers: { "Content-Type": "application/json", "x-master-key": token },
              body: JSON.stringify({ name, email, location, status, balance: parseFloat(balance), avatar })
          });
          if (res.ok) {
              setIsDialogOpen(false);
              setName(""); setEmail(""); setLocation(""); setBalance("0"); setStatus("Active"); setAvatar("");
              fetchUsers();
          }
      } catch (e) {}
      setSaving(false);
  };

  const totalBalance = users.reduce((acc, user) => acc + (user.balance || 0), 0);

  return (
    <div className="bg-white dark:bg-[#252525] border border-neutral-200 dark:border-[#333] rounded-xl shadow-sm overflow-hidden flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-neutral-200 dark:border-[#333] flex items-center justify-between">
        <div>
          <h3 className="text-neutral-900 dark:text-white font-medium">Usuarios del Sistema</h3>
          <p className="text-neutral-500 dark:text-[#888] text-sm">Gestiona los usuarios y verifica su estado y balance.</p>
        </div>
        <div className="flex items-center gap-2">
            <button onClick={fetchUsers} className="p-2 bg-neutral-100 dark:bg-[#1e1e1e] hover:bg-neutral-200 dark:hover:bg-[#333] rounded-md transition-colors text-neutral-600 dark:text-white">
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <Dialog.Root open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <Dialog.Trigger asChild>
                <button className="flex items-center gap-2 px-3 py-1.5 bg-[#e05a2b] text-white text-sm font-medium rounded-md hover:bg-[#c94e24] transition-colors">
                  <Plus className="w-4 h-4" /> Add User
                </button>
              </Dialog.Trigger>
              <Dialog.Portal>
                <Dialog.Overlay className="fixed inset-0 bg-black/60 z-50" />
                <Dialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-white dark:bg-[#1e1e1e] border border-neutral-200 dark:border-[#333] rounded-[12px] shadow-xl p-6 z-50">
                  <div className="flex items-center justify-between mb-6">
                    <Dialog.Title className="text-lg font-semibold text-neutral-900 dark:text-white">Registrar Usuario</Dialog.Title>
                    <Dialog.Close asChild>
                      <button className="text-neutral-500 hover:text-neutral-900 dark:hover:text-white"><X className="w-5 h-5"/></button>
                    </Dialog.Close>
                  </div>
                  
                  <form onSubmit={handleCreateUser} className="space-y-4">

                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-full overflow-hidden bg-neutral-100 dark:bg-[#252525] border border-neutral-200 dark:border-[#333] flex items-center justify-center text-xl font-medium">
                            {avatar ? <img src={avatar} alt="Avatar" className="w-full h-full object-cover" /> : (name.charAt(0) || "U")}
                        </div>
                        <button type="button" onClick={() => setShowAvatars(!showAvatars)} className="text-[12px] text-[#e05a2b] hover:underline font-medium">Choose Avatar</button>
                    </div>
                    {showAvatars && (
                        <div className="p-3 bg-neutral-50 dark:bg-[#252525] border border-neutral-200 dark:border-[#333] rounded-[8px] w-full mt-2">
                            <div className="grid grid-cols-6 gap-2 max-h-32 overflow-y-auto custom-scrollbar">
                                {presetAvatars.map((url, i) => (
                                    <img key={i} src={url} alt={`Avatar ${i}`} className="w-8 h-8 rounded-full cursor-pointer hover:ring-2 ring-[#e05a2b] transition-all" onClick={() => { setAvatar(url); setShowAvatars(false); }} />
                                ))}
                            </div>
                        </div>
                    )}

                    <div>
                        <label className="block text-[12px] font-medium text-neutral-700 dark:text-[#888] mb-1">Full Name</label>
                        <input required type="text" value={name} onChange={e => setName(e.target.value)} className="w-full bg-neutral-50 dark:bg-[#252525] border border-neutral-200 dark:border-[#333] rounded-md px-3 py-2 text-sm text-neutral-900 dark:text-white focus:outline-none focus:border-[#e05a2b]" placeholder="John Doe" />
                    </div>
                    <div>
                        <label className="block text-[12px] font-medium text-neutral-700 dark:text-[#888] mb-1">Email</label>
                        <input required type="email" value={email} onChange={e => setEmail(e.target.value)} className="w-full bg-neutral-50 dark:bg-[#252525] border border-neutral-200 dark:border-[#333] rounded-md px-3 py-2 text-sm text-neutral-900 dark:text-white focus:outline-none focus:border-[#e05a2b]" placeholder="john@example.com" />
                    </div>
                    <div>
                        <label className="block text-[12px] font-medium text-neutral-700 dark:text-[#888] mb-1">Location</label>
                        <input type="text" value={location} onChange={e => setLocation(e.target.value)} className="w-full bg-neutral-50 dark:bg-[#252525] border border-neutral-200 dark:border-[#333] rounded-md px-3 py-2 text-sm text-neutral-900 dark:text-white focus:outline-none focus:border-[#e05a2b]" placeholder="Madrid, Spain" />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-[12px] font-medium text-neutral-700 dark:text-[#888] mb-1">Status</label>
                            <select value={status} onChange={e => setStatus(e.target.value)} className="w-full bg-neutral-50 dark:bg-[#252525] border border-neutral-200 dark:border-[#333] rounded-md px-3 py-2 text-sm text-neutral-900 dark:text-white focus:outline-none focus:border-[#e05a2b]">
                                <option>Active</option>
                                <option>Inactive</option>
                                <option>Suspended</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-[12px] font-medium text-neutral-700 dark:text-[#888] mb-1">Balance</label>
                            <input type="number" step="0.01" value={balance} onChange={e => setBalance(e.target.value)} className="w-full bg-neutral-50 dark:bg-[#252525] border border-neutral-200 dark:border-[#333] rounded-md px-3 py-2 text-sm text-neutral-900 dark:text-white focus:outline-none focus:border-[#e05a2b]" placeholder="0.00" />
                        </div>
                    </div>
                    
                    <div className="flex justify-end gap-3 mt-6">
                        <Dialog.Close asChild>
                            <button type="button" className="px-4 py-2 text-sm text-neutral-600 dark:text-[#ccc] hover:bg-neutral-100 dark:hover:bg-[#333] rounded-md transition-colors">Cancel</button>
                        </Dialog.Close>
                        <button type="submit" disabled={saving} className="px-4 py-2 bg-[#e05a2b] text-white text-sm font-medium rounded-md hover:bg-[#c94e24] transition-colors disabled:opacity-50">
                            {saving ? 'Saving...' : 'Registrar'}
                        </button>
                    </div>
                  </form>
                </Dialog.Content>
              </Dialog.Portal>
            </Dialog.Root>
        </div>
      </div>

      {/* Table Content */}
      <div className="flex-1 overflow-auto custom-scrollbar">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead className="sticky top-0 bg-neutral-50 dark:bg-[#1e1e1e] border-b border-neutral-200 dark:border-[#333] text-neutral-500 dark:text-[#888] font-medium">
            <tr>
              <th className="px-4 py-3 font-medium">Name</th>
              <th className="px-4 py-3 font-medium">Email</th>
              <th className="px-4 py-3 font-medium hidden md:table-cell">Location</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium text-right">Balance</th>
              <th className="px-4 py-3 font-medium text-center">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100 dark:divide-[#2e2e2e]">
            {loading ? (
                <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-neutral-500">Loading users...</td>
                </tr>
            ) : users.length === 0 ? (
                <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-neutral-500">No hay usuarios registrados. Usa &quot;Add User&quot;.</td>
                </tr>
            ) : (
                users.map((user, i) => (
                    <tr key={i} className="hover:bg-neutral-50 dark:hover:bg-[#1e1e1e]/50 transition-colors">
                        <td className="px-4 py-3 font-medium text-neutral-900 dark:text-white">
                        <div className="flex items-center gap-3">
                            
                            <div className="w-7 h-7 rounded-full bg-neutral-200 dark:bg-[#333] flex items-center justify-center text-xs font-bold text-neutral-600 dark:text-[#ccc] overflow-hidden">
                            {user.avatar ? <img src={user.avatar} className="w-full h-full object-cover"/> : user.name.charAt(0)}
                            </div>

                            {user.name}
                        </div>
                        </td>
                        <td className="px-4 py-3 text-neutral-600 dark:text-[#aaa]">{user.email}</td>
                        <td className="px-4 py-3 text-neutral-500 dark:text-[#888] hidden md:table-cell">{user.location}</td>
                        <td className="px-4 py-3">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${
                            user.status === 'Active' 
                            ? 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-500/20'
                            : user.status === 'Suspended'
                            ? 'bg-red-50 dark:bg-red-500/10 text-red-700 dark:text-red-400 border-red-200 dark:border-red-500/20'
                            : 'bg-neutral-100 dark:bg-neutral-500/10 text-neutral-700 dark:text-neutral-400 border-neutral-200 dark:border-neutral-500/20'
                        }`}>
                            {user.status}
                        </span>
                        </td>
                        <td className={`px-4 py-3 text-right font-medium ${
                        user.balance < 0 ? 'text-red-600 dark:text-red-400' : 'text-neutral-900 dark:text-white'
                        }`}>
                        {user.balance < 0 ? '-' : ''}${Math.abs(user.balance).toLocaleString('en-US', {minimumFractionDigits: 2})}
                        </td>
                        <td className="px-4 py-3 text-center">
                        <button className="text-[#e05a2b] hover:underline text-[13px]">Details</button>
                        </td>
                    </tr>
                ))
            )}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-neutral-200 dark:border-[#333] bg-neutral-50 dark:bg-[#1e1e1e] flex items-center justify-between text-sm">
        <span className="text-neutral-500 dark:text-[#888]">Total Users: <strong className="text-neutral-900 dark:text-white font-medium">{users.length}</strong></span>
        <span className="text-neutral-900 dark:text-white font-medium">${totalBalance.toLocaleString('en-US', {minimumFractionDigits: 2})}</span>
      </div>
    </div>
  );
}
