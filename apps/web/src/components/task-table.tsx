"use client";

import type { TaskItem } from "@/lib/api";

interface TaskTableProps {
  tasks: TaskItem[];
}

function PriorityBadge({ priority }: { priority: string }) {
  const colors: Record<string, string> = {
    high: "bg-red-900 text-red-300",
    medium: "bg-yellow-900 text-yellow-300",
    low: "bg-green-900 text-green-300",
  };
  return (
    <span
      className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${colors[priority] || "bg-gray-700 text-gray-300"}`}
    >
      {priority}
    </span>
  );
}

export function TaskTable({ tasks }: TaskTableProps) {
  if (!tasks.length) return null;

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
      <h2 className="mb-4 text-lg font-semibold">Tasks</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-gray-800 text-gray-400">
              <th className="pb-2 pr-4">#</th>
              <th className="pb-2 pr-4">Title</th>
              <th className="pb-2 pr-4">Priority</th>
              <th className="pb-2 pr-4">Hours</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => (
              <tr
                key={task.order_index}
                className="border-b border-gray-800/50"
              >
                <td className="py-2 pr-4 text-gray-500">
                  {task.order_index}
                </td>
                <td className="py-2 pr-4">
                  <div className="font-medium">{task.title}</div>
                  <div className="mt-0.5 text-xs text-gray-400">
                    {task.description}
                  </div>
                </td>
                <td className="py-2 pr-4">
                  <PriorityBadge priority={task.priority} />
                </td>
                <td className="py-2 pr-4 text-gray-400">
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
