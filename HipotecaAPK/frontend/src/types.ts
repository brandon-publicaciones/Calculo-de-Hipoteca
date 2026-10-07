export interface CalcRequest {
  property_value: number;
  housing_type: "nueva" | "usada";
  region: 1 | 2 | null;
  down_payment_mode: "percent" | "amount";
  down_payment: number;
  years: number;
  promo_rate: number | null;
  promo_years: number | null;
  commercial_rate: number;
}

export interface Row {
  month: number; rate: number; payment: number; interest: number;
  principal: number; balance: number; preferential: boolean;
}

export interface CalcResult {
  property_value: number; down_payment: number; loan_amount: number; years: number;
  commercial_rate: number; subsidy_applies: boolean; subsidy_points: number; subsidy_years: number;
  tramo: number | null; preferential_rate: number | null; preferential_months: number;
  preferential_payment: number | null; regular_payment: number | null; regular_months: number;  effective_commercial_rate: number;
  effective_preferential_rate: number | null;
  manual_promo: boolean;
  total_interest: number; total_paid: number; note: string; schedule: Row[];
}
