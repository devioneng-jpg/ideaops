"use client";

import type { TaskItem } from "@/lib/api";

interface TaskTableProps {
  tasks: TaskItem[];
}

function PriorityBadge({ priority }: { priority: string }) {
  const styles: Record<string, string> = {
    high: "border-red-500/20 bg-red-500/[0.08] text-red-400",
    medium: "border-yellow-500/20 bg-yellow-500/[0.08] text-yellow-400",
    low: "border-emerald-500/20 bg-emerald-500/[0.08] text-emerald-400",
  };
  return (
    <span
      className={`inline-block rounded-full border px-2 py-0.5 text-[11px] font-medium ${styles[priority] || "border-white/10 bg-white/5 text-gray-400"}`}
    >
      {priority}
    </span>
  );
}

export function TaskTable({ tasks }: TaskTableProps) {
  if (!tasks.length) return null;

  return (
    <div className="card gradient-border rounded-xl p-6">
      <h2 className="mb-5 text-lg font-semibold tracking-tight">Tasks</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-white/[0.06] text-xs font-medium uppercase tracking-wider text-gray-500">
              <th className="pb-3 pr-4">#</th>
              <th className="pb-3 pr-4">Title</th>
              <th className="pb-3 pr-4">Priority</th>
              <th className="pb-3 pr-4">Hours</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => (
              <tr
                key={task.order_index}
                className="border-b border-white/[0.04] transition-colors hover:bg-white/[0.02]"
              >
                <td className="py-3 pr-4 text-gray-500">{task.order_index}</td>
                <td className="py-3 pr-4">
                  <div className="font-medium text-gray-200">{task.title}</div>
                  <div className="mt-0.5 text-xs leading-relaxed text-gray-500">
                    {task.description}
                  </div>
                </td>
                <td className="py-3 pr-4">
                  <PriorityBadge priority={task.priority} />
                </td>
                <td className="py-3 pr-4 tabular-nums text-gray-400">
                  {task.estimated_hours}h
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
