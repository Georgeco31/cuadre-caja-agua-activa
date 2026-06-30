export type DenominationType = "coin" | "bill";

export type Denomination = {
  id: number;
  type: DenominationType;
  value: string;
  label: string;
  is_active: boolean;
};
