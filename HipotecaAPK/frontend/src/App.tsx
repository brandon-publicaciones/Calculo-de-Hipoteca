import { useState } from "react";
import { calculate, downloadPdf } from "./api";
import type { CalcRequest, CalcResult } from "./types";

const usd = (n: number | null) =>
  n === null ? "—" : n.toLocaleString("en-US", { style: "currency", currency: "USD" });

const tea = (nominal: number) => ((1 + nominal / 1200) ** 12 - 1) * 100;

export default function App() {
  const [f, setF] = useState({
    value: "100000", type: "nueva", region: "1", mode: "percent", down: "10", years: "30", rate: "7",
    promoRate: "6.5", promoYears: "7",
  });
  const [res, setRes] = useState<CalcResult | null>(null);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const [showAll, setShowAll] = useState(false);
  const [manual, setManual] = useState(false);

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setF({ ...f, [k]: e.target.value });

  const body = (): CalcRequest => ({
    property_value: Number(f.value),
    housing_type: f.type as "nueva" | "usada",
    region: f.type === "nueva" ? (Number(f.region) as 1 | 2) : null,
    down_payment_mode: f.mode as "percent" | "amount",
    down_payment: Number(f.down),
    years: Number(f.years),
    commercial_rate: Number(f.rate),
    promo_rate: manual ? Number(f.promoRate) : null,
    promo_years: manual ? Number(f.promoYears) : null,
  });

  const run = async (fn: () => Promise<void>) => {
    setErr(""); setBusy(true);
    try { await fn(); } catch (e) { setErr((e as Error).message); } finally { setBusy(false); }
  };

  const price = Number(f.value) || 0;
  const downNum = Number(f.down) || 0;
  const downAmount = f.mode === "percent" ? (price * downNum) / 100 : downNum;
  const downPercent = price > 0 ? (downAmount / price) * 100 : 0;
  const loanAmount = price - downAmount;
  const rows = res ? (showAll ? res.schedule : res.schedule.slice(0, 12)) : [];

  return (
    <main>
      <h1>🏠 Hipoteca Panamá 2026</h1>
      <p className="sub">Leyes 468 y 481 de 2025 · Interés preferencial</p>

      <form className="card grid" onSubmit={(e) => { e.preventDefault(); run(async () => setRes(await calculate(body()))); }}>
        <label>Valor de la propiedad (USD)
          <input type="number" min="1" step="any" value={f.value} onChange={set("value")} required /></label>

        <label>Tipo de vivienda
          <select value={f.type} onChange={set("type")}>
            <option value="nueva">Nueva (residencia principal)</option>
            <option value="usada">Usada / segunda mano</option></select></label>

        {f.type === "nueva" && (
          <label>Región
            <select value={f.region} onChange={set("region")}>
              <option value="1">Región 1 – Panamá y Panamá Oeste</option>
              <option value="2">Región 2 – Colón, Chiriquí (David) y resto del país</option></select></label>
        )}

        <label>Abono inicial
          <div className="row">
            <input type="number" min="0" step="any" value={f.down} onChange={set("down")} required />
            <select value={f.mode} onChange={set("mode")}>
              <option value="percent">%</option>
              <option value="amount">USD</option>
            </select>
          </div>
          <small>
            {f.mode === "percent"
              ? <>Abono: <b>{usd(downAmount)}</b></>
              : <>Equivale a: <b>{downPercent.toFixed(2)}%</b></>}
            {" · "}Financiado: <b>{usd(loanAmount)}</b>
          </small>
        </label>

        <label>Plazo (años)
          <input type="number" min="1" max="40" value={f.years} onChange={set("years")} required /></label>

        <label>Tasa nominal comercial (TNA, % anual)
          <input type="number" min="0.01" step="0.01" value={f.rate} onChange={set("rate")} required />
          <small>Efectiva (TEA): <b>{tea(Number(f.rate) || 0).toFixed(2)}%</b></small></label>

        <label className="check">
          <input type="checkbox" checked={manual} onChange={(e) => setManual(e.target.checked)} />
          Editar tasa promocional manualmente</label>

        {manual && (<>
          <label>Tasa nominal promocional (TNA, % anual)
            <input type="number" min="0" step="0.01" value={f.promoRate} onChange={set("promoRate")} required />
            <small>Efectiva (TEA): <b>{tea(Number(f.promoRate) || 0).toFixed(2)}%</b></small></label>
          <label>Años de tasa promocional
            <input type="number" min="1" max="40" value={f.promoYears} onChange={set("promoYears")} required /></label>
        </>)}

        <button disabled={busy}>{busy ? "Calculando…" : "Calcular"}</button>
      </form>

      {err && <p className="err">{err}</p>}

      {res && (<>
        <p className="note">{res.note}</p>
        <section className="results">
          {res.subsidy_applies && (
            <div className="card pref">
              <h2>Letra Mensual con Interés Preferencial</h2>
              <strong>{usd(res.preferential_payment)}</strong>
              <small>{res.preferential_rate?.toFixed(2)}% durante {res.preferential_months / 12} años
                {res.manual_promo ? " (tasa manual)" : ` (${res.subsidy_points}% de subsidio)`}
                {" · "}TEA {res.effective_preferential_rate?.toFixed(2)}%</small>
            </div>)}
          <div className="card reg">
            <h2>Letra Mensual Regular</h2>
            <strong>{usd(res.regular_payment)}</strong>
            <small>{res.commercial_rate.toFixed(2)}% durante {res.regular_months / 12} años
              {res.subsidy_applies ? " (tras la promoción)" : ""}
              {" · "}TEA {res.effective_commercial_rate.toFixed(2)}%</small>
          </div>
        </section>

        <div className="card stats">
          <span>Monto financiado: <b>{usd(res.loan_amount)}</b></span>
          <span>Abono: <b>{usd(res.down_payment)}</b></span>
          <span>Intereses totales: <b>{usd(res.total_interest)}</b></span>
          <span>Total pagado: <b>{usd(res.total_paid)}</b></span>
        </div>

        <button className="alt" disabled={busy} onClick={() => run(() => downloadPdf(body()))}>
          ⬇ Descargar tabla de amortización (PDF)</button>

        <div className="scroll">
          <table>
            <thead><tr><th>Mes</th><th>Tasa</th><th>Letra</th><th>Interés</th><th>Capital</th><th>Saldo</th></tr></thead>
            <tbody>{rows.map((r) => (
              <tr key={r.month} className={r.preferential ? "p" : ""}>
                <td>{r.month}</td><td>{r.rate.toFixed(2)}%</td><td>{usd(r.payment)}</td>
                <td>{usd(r.interest)}</td><td>{usd(r.principal)}</td><td>{usd(r.balance)}</td></tr>))}
            </tbody>
          </table>
        </div>
        <button className="link" onClick={() => setShowAll(!showAll)}>
          {showAll ? "Mostrar menos" : `Ver los ${res.schedule.length} meses`}</button>
      </>)}
      <p className="foot">Simulación referencial. Confirme tasas y condiciones con su banco.</p>
    </main>
  );
}