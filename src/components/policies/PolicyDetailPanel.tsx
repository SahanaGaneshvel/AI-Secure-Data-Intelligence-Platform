import React, { useState, useEffect } from "react";
import { Policy } from "@/lib/types";
import { X } from "lucide-react";
import { RiskBadge } from "@/components/shared/RiskBadge";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { Button } from "@/components/shared/Button";

interface PolicyDetailPanelProps {
  policy: Policy | null;
  onClose: () => void;
  onSave: (policy: Policy) => void;
}

export const PolicyDetailPanel: React.FC<PolicyDetailPanelProps> = ({
  policy,
  onClose,
  onSave,
}) => {
  const [editedPolicy, setEditedPolicy] = useState<Policy | null>(null);

  useEffect(() => {
    setEditedPolicy(policy);
  }, [policy]);

  if (!policy || !editedPolicy) return null;

  const handleSave = () => {
    onSave(editedPolicy);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-2xl rounded-lg border border-slate-800 bg-slate-900 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-800 p-6">
          <div>
            <h2 className="text-xl font-bold text-white">{policy.name}</h2>
            <p className="mt-1 text-sm text-slate-400">{policy.description}</p>
          </div>
          <button
            onClick={onClose}
            className="rounded p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">Status</label>
              <StatusBadge status={editedPolicy.status} size="md" />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">
                Severity Threshold
              </label>
              <RiskBadge level={editedPolicy.severityThreshold} size="md" />
            </div>
          </div>

          <div>
            <label className="mb-3 block text-sm font-medium text-slate-300">Actions</label>
            <div className="space-y-3">
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={editedPolicy.maskingEnabled}
                  onChange={(e) =>
                    setEditedPolicy({ ...editedPolicy, maskingEnabled: e.target.checked })
                  }
                  className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                />
                <span className="text-sm text-slate-300">Enable Masking</span>
              </label>
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={editedPolicy.blockingEnabled}
                  onChange={(e) =>
                    setEditedPolicy({ ...editedPolicy, blockingEnabled: e.target.checked })
                  }
                  className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                />
                <span className="text-sm text-slate-300">Enable Blocking</span>
              </label>
            </div>
          </div>

          <div>
            <label className="mb-3 block text-sm font-medium text-slate-300">Detectors</label>
            <div className="grid grid-cols-2 gap-3">
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={editedPolicy.detectors.regex}
                  onChange={(e) =>
                    setEditedPolicy({
                      ...editedPolicy,
                      detectors: { ...editedPolicy.detectors, regex: e.target.checked },
                    })
                  }
                  className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                />
                <span className="text-sm text-slate-300">Regex</span>
              </label>
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={editedPolicy.detectors.heuristic}
                  onChange={(e) =>
                    setEditedPolicy({
                      ...editedPolicy,
                      detectors: { ...editedPolicy.detectors, heuristic: e.target.checked },
                    })
                  }
                  className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                />
                <span className="text-sm text-slate-300">Heuristic</span>
              </label>
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={editedPolicy.detectors.nlp}
                  onChange={(e) =>
                    setEditedPolicy({
                      ...editedPolicy,
                      detectors: { ...editedPolicy.detectors, nlp: e.target.checked },
                    })
                  }
                  className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                />
                <span className="text-sm text-slate-300">NLP</span>
              </label>
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={editedPolicy.detectors.ai}
                  onChange={(e) =>
                    setEditedPolicy({
                      ...editedPolicy,
                      detectors: { ...editedPolicy.detectors, ai: e.target.checked },
                    })
                  }
                  className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                />
                <span className="text-sm text-slate-300">AI</span>
              </label>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 border-t border-slate-800 p-6">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSave}>
            Save Changes
          </Button>
        </div>
      </div>
    </div>
  );
};
