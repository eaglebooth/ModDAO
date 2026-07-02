"use client";

import { useState, useEffect } from "react";
import { 
  connectWallet, 
  readContract, 
  writeContract, 
  ContractResult 
} from "@/lib/genlayer";
import { 
  Shield, 
  Coins, 
  UserPlus, 
  UserMinus, 
  FileText, 
  Cpu, 
  CheckCircle, 
  RefreshCw, 
  Terminal, 
  TrendingUp,
  AlertTriangle
} from "lucide-react";

interface Moderator {
  id: number;
  wallet: string;
  name: string;
  base_pay: number;
  active: boolean;
}

interface Evaluation {
  id: number;
  mod_id: number;
  log_url: string;
  score: number;
  payout: number;
  status: string;
  comment: string;
}

const DEFAULT_CONTRACT = "0xBbbc733490e7279A8113Dc5Cbdcc46b6C592b5D1";
const ZERO_ADDRESS = "0x0000000000000000000000000000000000000000";

const SCENARIOS = [
  {
    name: "Polite & Helpful",
    file: "mod_polite.txt",
    desc: "Mod Alex resolves Brave wallet connection errors politely and accurately."
  },
  {
    name: "Unhelpful & Lazy",
    file: "mod_lazy.txt",
    desc: "Mod Sam is slow to reply, lazy, and tells the user to check explorer themselves."
  },
  {
    name: "Toxic & Insulting",
    file: "mod_toxic.txt",
    desc: "Mod Chris calls the user an idiot and violates community moderator rules."
  }
];

export default function Home() {
  // Config States
  const [contractAddress, setContractAddress] = useState<string>(DEFAULT_CONTRACT);
  const [walletAccount, setWalletAccount] = useState<string>("");
  
  // Storage State
  const [adminAddress, setAdminAddress] = useState<string>("");
  const [treasuryBalance, setTreasuryBalance] = useState<number>(0);
  const [mods, setMods] = useState<Moderator[]>([]);
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  
  // Registration Inputs
  const [regWallet, setRegWallet] = useState<string>("0x70997970C51812dc3A010C7d01b50e0d17dc79C8");
  const [regName, setRegName] = useState<string>("Mod_Alex");
  const [regBasePay, setRegBasePay] = useState<string>("100");

  // Treasury Inputs
  const [refillAmount, setRefillAmount] = useState<string>("500");

  // Evaluation Inputs
  const [selectedModId, setSelectedModId] = useState<string>("");
  const [selectedScenarioIndex, setSelectedScenarioIndex] = useState<number>(0);
  const [rawLogPreview, setRawLogPreview] = useState<string>("");

  // UI Flow Status
  const [loading, setLoading] = useState<boolean>(false);
  const [statusText, setStatusText] = useState<string>("Disconnected. Connect wallet to read contract.");
  const [logs, setLogs] = useState<Array<{ time: string; msg: string }>>([]);

  // Log message helper
  function addLog(msg: string) {
    const time = new Date().toLocaleTimeString();
    setLogs((prev) => [{ time, msg }, ...prev]);
  }

  // Load contract address from localStorage or URL if present
  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const contractParam = searchParams.get("contract");
    if (contractParam) {
      setContractAddress(contractParam);
      addLog(`Loaded contract address from URL: ${contractParam}`);
    } else {
      const stored = localStorage.getItem("moddao_contract");
      if (stored) {
        setContractAddress(stored);
        addLog(`Loaded contract address from storage: ${stored}`);
      }
    }
  }, []);

  // Sync log preview
  useEffect(() => {
    fetchScenarioPreview(SCENARIOS[selectedScenarioIndex].file);
  }, [selectedScenarioIndex]);

  async function fetchScenarioPreview(filename: string) {
    try {
      const res = await fetch(`/scenarios/${filename}`);
      const text = await res.text();
      setRawLogPreview(text);
    } catch (err) {
      setRawLogPreview("Error loading scenario file preview.");
    }
  }

  // Reload Contract State
  async function loadContractState() {
    if (!contractAddress || contractAddress === ZERO_ADDRESS) {
      setStatusText("Contract address not configured.");
      return;
    }
    setStatusText("Loading state...");
    addLog("Fetching general state from contract...");
    
    const result = await readContract("get_contract_state", [], contractAddress);
    if (!result.success) {
      setStatusText(result.error || "Failed to load contract");
      addLog(`Error fetching state: ${result.error}`);
      return;
    }

    try {
      const state = JSON.parse(result.data as string);
      setAdminAddress(state.admin);
      setTreasuryBalance(state.treasury);
      const modCount = state.mod_count;
      const evalCount = state.eval_count;

      addLog(`Contract State: Treasury = ${state.treasury} USD | Mods = ${modCount} | Evals = ${evalCount}`);

      // Fetch Mods
      const fetchedMods: Moderator[] = [];
      for (let i = 0; i < modCount; i++) {
        const modRes = await readContract("get_moderator", [BigInt(i)], contractAddress);
        if (modRes.success) {
          const mod = JSON.parse(modRes.data as string);
          fetchedMods.push({
            id: mod.id,
            wallet: mod.wallet,
            name: mod.name,
            base_pay: mod.base_pay,
            active: mod.active === 1,
          });
        }
      }
      setMods(fetchedMods);
      if (fetchedMods.length > 0 && !selectedModId) {
        setSelectedModId(fetchedMods[0].id.toString());
      }

      // Fetch Evaluations
      const fetchedEvals: Evaluation[] = [];
      for (let i = 0; i < evalCount; i++) {
        const evalRes = await readContract("get_evaluation", [BigInt(i)], contractAddress);
        if (evalRes.success) {
          const ev = JSON.parse(evalRes.data as string);
          fetchedEvals.push({
            id: ev.id,
            mod_id: ev.mod_id,
            log_url: ev.log_url,
            score: ev.score,
            payout: ev.payout,
            status: ev.status,
            comment: ev.comment,
          });
        }
      }
      setEvaluations(fetchedEvals.reverse()); // Show newest first in UI

      setStatusText("Contract state successfully synced.");
    } catch (e) {
      setStatusText("Failed to parse contract state response.");
      addLog("Parsing error during state sync.");
    }
  }

  // Handle Wallet Connect
  async function handleConnectWallet() {
    setLoading(true);
    setStatusText("Connecting wallet...");
    const res = await connectWallet();
    setLoading(false);
    if (res.success) {
      setWalletAccount(res.data as string);
      setStatusText("Wallet connected. Ready to read/write.");
      addLog(`Connected Wallet: ${res.data}`);
      if (contractAddress && contractAddress !== ZERO_ADDRESS) {
        loadContractState();
      }
    } else {
      setStatusText(res.error || "Failed to connect wallet");
      addLog(`Wallet connection error: ${res.error}`);
    }
  }

  // Save Contract Config
  function saveContractConfig(addr: string) {
    setContractAddress(addr);
    localStorage.setItem("moddao_contract", addr);
    addLog(`Saved new contract address configuration: ${addr}`);
    loadContractState();
  }

  // Helper to handle transactions
  async function runTransaction(
    title: string,
    funcName: string,
    args: unknown[]
  ) {
    setLoading(true);
    setStatusText(`Executing ${title}...`);
    addLog(`Sending transaction: ${funcName}...`);
    
    const result = await writeContract(funcName, args, contractAddress);
    setLoading(false);
    
    if (result.success) {
      addLog(`Tx SUCCESS: ${title} | Hash: ${result.hash}`);
      setStatusText(`${title} completed successfully.`);
      await loadContractState();
    } else {
      addLog(`Tx FAILED: ${result.error}`);
      setStatusText(`Transaction failed: ${result.error}`);
    }
  }

  // Actions
  function initializeContract() {
    runTransaction("Initialize Contract", "initialize", [walletAccount]);
  }

  function addFunds() {
    runTransaction("Add Funds to Treasury", "add_funds", [BigInt(refillAmount)]);
  }

  function registerModerator() {
    runTransaction("Register Moderator", "register_moderator", [
      regWallet,
      regName,
      BigInt(regBasePay)
    ]);
  }

  function deactivateMod(id: number) {
    runTransaction("Deactivate Moderator", "deactivate_moderator", [BigInt(id)]);
  }

  function submitEvaluation() {
    // Determine local scenarios file URL based on current host
    const origin = window.location.origin;
    const logUrl = `${origin}/scenarios/${SCENARIOS[selectedScenarioIndex].file}`;
    addLog(`Submitting evaluation request. Log URL: ${logUrl}`);
    runTransaction("Submit Support Log", "request_evaluation", [
      BigInt(selectedModId),
      logUrl
    ]);
  }

  function triggerAiEvaluation(id: number) {
    runTransaction(`AI Jury Evaluation Ticket #${id}`, "evaluate", [BigInt(id)]);
  }

  function shortAddress(addr: string) {
    if (!addr) return "";
    return `${addr.substring(0, 6)}...${addr.substring(addr.length - 4)}`;
  }

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div className="brand-section">
          <h1>ModDAO</h1>
          <p>Automated Quality-Based Payroll for Community Support Teams</p>
        </div>
        
        <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
          {walletAccount ? (
            <button className="btn-wallet connected" onClick={handleConnectWallet}>
              <CheckCircle size={16} />
              {shortAddress(walletAccount)}
            </button>
          ) : (
            <button className="btn-wallet" onClick={handleConnectWallet} disabled={loading}>
              <Shield size={16} />
              Connect Wallet
            </button>
          )}
        </div>
      </header>

      {/* Network / Config bar */}
      <div className="card-module" style={{ marginBottom: "2rem", padding: "1rem 1.75rem" }}>
        <div style={{ display: "flex", gap: "1.5rem", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap" }}>
          <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
            <span style={{ fontSize: "0.85rem", fontWeight: "600", color: "var(--text-muted)" }}>Contract Address:</span>
            <input 
              type="text" 
              className="form-input" 
              style={{ width: "380px", padding: "0.4rem 0.75rem", fontSize: "0.85rem" }}
              value={contractAddress}
              onChange={(e) => setContractAddress(e.target.value)}
              placeholder="0x..."
            />
            <button className="btn-wallet" style={{ padding: "0.4rem 1rem", fontSize: "0.85rem" }} onClick={() => saveContractConfig(contractAddress)}>
              Apply
            </button>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            {contractAddress === ZERO_ADDRESS && (
              <span style={{ color: "var(--warning)", fontSize: "0.8rem", display: "flex", alignItems: "center", gap: "0.25rem" }}>
                <AlertTriangle size={14} /> Please deploy the contract and configure its address
              </span>
            )}
            <button className="btn-wallet" style={{ padding: "0.4rem 1rem", fontSize: "0.85rem" }} onClick={loadContractState} disabled={loading || contractAddress === ZERO_ADDRESS}>
              <RefreshCw size={14} className={loading ? "animate-spin" : ""} /> Sync State
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="dashboard-grid">
        {/* Left Column */}
        <div className="dashboard-panel">
          
          {/* Treasury Management */}
          <div className="card-module">
            <h3 className="card-title">
              <Coins size={18} style={{ color: "var(--primary)" }} />
              DAO Treasury & Config
            </h3>
            
            <div className="stats-list" style={{ marginBottom: "1.5rem" }}>
              <div className="stat-item">
                <span className="stat-label">Admin/Owner</span>
                <span className="stat-value" style={{ fontSize: "0.9rem" }}>
                  {adminAddress ? shortAddress(adminAddress) : "Not Initialized"}
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Treasury Budget</span>
                <span className="stat-value highlight">{treasuryBalance} USD</span>
              </div>
            </div>

            {!adminAddress ? (
              <button 
                className="btn-primary" 
                onClick={!walletAccount ? handleConnectWallet : initializeContract} 
                disabled={loading || (!!walletAccount && contractAddress === ZERO_ADDRESS)}
              >
                {!walletAccount 
                  ? "Connect Wallet to Initialize" 
                  : contractAddress === ZERO_ADDRESS 
                    ? "Configure Contract Address First" 
                    : "Initialize Contract Admin"}
              </button>
            ) : (
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <input 
                  type="number" 
                  className="form-input" 
                  value={refillAmount} 
                  onChange={(e) => setRefillAmount(e.target.value)} 
                  placeholder="Amount"
                />
                <button className="btn-primary" onClick={addFunds} disabled={loading || !walletAccount} style={{ width: "120px" }}>
                  Add Funds
                </button>
              </div>
            )}
          </div>

          {/* Moderator Registration */}
          <div className="card-module">
            <h3 className="card-title">
              <UserPlus size={18} style={{ color: "var(--primary)" }} />
              Register Moderator
            </h3>
            
            <div className="form-group">
              <label className="form-label">Moderator Wallet Address</label>
              <input 
                type="text" 
                className="form-input" 
                value={regWallet} 
                onChange={(e) => setRegWallet(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Discord/Telegram Username</label>
              <input 
                type="text" 
                className="form-input" 
                value={regName} 
                onChange={(e) => setRegName(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Weekly Base Pay (USD)</label>
              <input 
                type="number" 
                className="form-input" 
                value={regBasePay} 
                onChange={(e) => setRegBasePay(e.target.value)}
              />
            </div>

            <button 
              className="btn-primary" 
              onClick={!walletAccount ? handleConnectWallet : registerModerator} 
              disabled={loading || (!!walletAccount && (!adminAddress || contractAddress === ZERO_ADDRESS))}
            >
              {!walletAccount 
                ? "Connect Wallet to Register" 
                : contractAddress === ZERO_ADDRESS 
                  ? "Configure Contract Address First" 
                  : !adminAddress 
                    ? "Initialize Contract Admin First" 
                    : "Register New Mod"}
            </button>
          </div>

          {/* Registered Moderators List */}
          <div className="card-module">
            <h3 className="card-title">
              <Shield size={18} style={{ color: "var(--primary)" }} />
              Active Moderator Team
            </h3>

            {mods.length === 0 ? (
              <div className="no-data">
                <span>No moderators registered yet</span>
              </div>
            ) : (
              <div className="list-container">
                {mods.map((mod) => (
                  <div key={mod.id} className="list-item">
                    <div className="item-info">
                      <h4>{mod.name}</h4>
                      <p>Wallet: {shortAddress(mod.wallet)}</p>
                      <p style={{ color: "var(--primary)", fontWeight: "600", fontSize: "0.85rem", marginTop: "0.25rem" }}>
                        Base Pay: {mod.base_pay} USD
                      </p>
                    </div>
                    <div>
                      {mod.active ? (
                        <button 
                          className="btn-wallet" 
                          style={{ borderColor: "var(--danger)", color: "var(--danger)", padding: "0.3rem 0.75rem", fontSize: "0.8rem", boxShadow: "none" }}
                          onClick={() => deactivateMod(mod.id)}
                          disabled={loading || !walletAccount}
                        >
                          <UserMinus size={12} /> Deactivate
                        </button>
                      ) : (
                        <span className="badge badge-inactive">Inactive</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>

        {/* Right Column */}
        <div className="dashboard-panel">
          
          {/* Submit Log / Ticket */}
          <div className="card-module">
            <h3 className="card-title">
              <FileText size={18} style={{ color: "var(--primary)" }} />
              Submit Support Log for AI Audit
            </h3>

            <div className="form-group">
              <label className="form-label">Select Moderator</label>
              <select 
                className="form-input" 
                value={selectedModId} 
                onChange={(e) => setSelectedModId(e.target.value)}
              >
                {mods.filter(m => m.active).map(mod => (
                  <option key={mod.id} value={mod.id}>{mod.name} (Base Pay: {mod.base_pay} USD)</option>
                ))}
                {mods.filter(m => m.active).length === 0 && (
                  <option>Register moderators first</option>
                )}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Select support quality scenario log</label>
              <div className="scenario-selector">
                {SCENARIOS.map((sc, index) => (
                  <button 
                    key={index} 
                    className={`scenario-btn ${selectedScenarioIndex === index ? "active" : ""}`}
                    onClick={() => setSelectedScenarioIndex(index)}
                  >
                    {sc.name}
                  </button>
                ))}
              </div>
              <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "0.5rem" }}>
                {SCENARIOS[selectedScenarioIndex].desc}
              </p>
              <div className="scenario-preview">
                {rawLogPreview}
              </div>
            </div>

            <button 
              className="btn-primary" 
              onClick={!walletAccount ? handleConnectWallet : submitEvaluation}
              disabled={loading || (!!walletAccount && (!selectedModId || mods.filter(m => m.active).length === 0 || contractAddress === ZERO_ADDRESS))}
            >
              {!walletAccount 
                ? "Connect Wallet to Submit" 
                : contractAddress === ZERO_ADDRESS 
                  ? "Configure Contract Address First" 
                  : mods.filter(m => m.active).length === 0 
                    ? "Register a Moderator First" 
                    : "Request AI Evaluation Ticket"}
            </button>
          </div>

          {/* Evaluations Queue */}
          <div className="card-module" style={{ flexGrow: 1 }}>
            <h3 className="card-title">
              <Cpu size={18} style={{ color: "var(--primary)" }} />
              Payroll & AI Evaluation Queue
            </h3>

            {evaluations.length === 0 ? (
              <div className="no-data">
                <span>No audit tickets submitted yet</span>
              </div>
            ) : (
              <div className="list-container" style={{ maxHeight: "600px" }}>
                {evaluations.map((ev) => {
                  const mod = mods.find(m => m.id === ev.mod_id);
                  const logFileName = ev.log_url.split("/").pop();
                  return (
                    <div key={ev.id} className="card-module" style={{ background: "rgba(10, 14, 20, 0.4)", padding: "1.25rem", marginBottom: "1rem" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                        <div>
                          <h4 style={{ color: "#ffffff", fontWeight: "600" }}>
                            Ticket #{ev.id} - Mod: {mod ? mod.name : `ID: ${ev.mod_id}`}
                          </h4>
                          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                            Log Source: {logFileName}
                          </span>
                        </div>
                        <div>
                          <span className={`badge badge-${ev.status.toLowerCase()}`}>{ev.status}</span>
                        </div>
                      </div>

                      {ev.status === "PENDING" ? (
                        <div style={{ display: "flex", justifyContent: "flex-end" }}>
                          <button 
                            className="btn-primary" 
                            style={{ width: "auto", fontSize: "0.85rem", padding: "0.5rem 1rem" }}
                            onClick={() => triggerAiEvaluation(ev.id)}
                            disabled={loading || !walletAccount}
                          >
                            <Cpu size={14} /> Start AI Evaluation & Payout
                          </button>
                        </div>
                      ) : ev.status === "APPROVED" ? (
                        <div style={{ background: "rgba(20, 184, 166, 0.05)", border: "1px solid rgba(20, 184, 166, 0.2)", borderRadius: "8px", padding: "0.75rem" }}>
                          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "0.5rem" }}>
                            <span style={{ color: "var(--text-muted)" }}>AI Quality Score:</span>
                            <span style={{ fontWeight: "700", color: "var(--primary)" }}>{ev.score}/100</span>
                          </div>
                          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "0.5rem" }}>
                            <span style={{ color: "var(--text-muted)" }}>Disbursed Reward:</span>
                            <span style={{ fontWeight: "700", color: "var(--accent)" }}>{ev.payout} USD</span>
                          </div>
                          <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", borderTop: "1px solid rgba(255,255,255,0.05)", paddingTop: "0.5rem", marginTop: "0.5rem", fontStyle: "italic" }}>
                            " {ev.comment} "
                          </div>
                        </div>
                      ) : (
                        <div style={{ background: "rgba(239, 44, 68, 0.05)", border: "1px solid rgba(239, 44, 68, 0.2)", borderRadius: "8px", padding: "0.75rem", fontSize: "0.8rem", color: "var(--danger)" }}>
                          Evaluation {ev.status}: {ev.comment}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Developer Console Log */}
          <div className="card-module" style={{ height: "200px" }}>
            <h3 className="card-title" style={{ fontSize: "0.95rem" }}>
              <Terminal size={14} style={{ color: "var(--primary)" }} />
              Developer System Console
            </h3>
            <div className="log-panel">
              {logs.map((log, index) => (
                <div key={index} className="log-entry">
                  <span className="log-time">[{log.time}]</span>
                  <span>{log.msg}</span>
                </div>
              ))}
              {logs.length === 0 && (
                <div style={{ color: "var(--text-muted)", fontStyle: "italic" }}>Console initialized... Connect wallet to start logs.</div>
              )}
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "0.75rem" }}>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", fontWeight: "500" }}>
                Status: {statusText}
              </span>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
