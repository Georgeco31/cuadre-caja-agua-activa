import type { DenominationType } from "@/types/denomination";

export type CountItemDetail = {
  id: number;
  cash_session_id: number;
  denomination_id: number;
  denomination_type: DenominationType;
  denomination_label: string;
  denomination_value: string;
  quantity: number;
  subtotal: string;
};
