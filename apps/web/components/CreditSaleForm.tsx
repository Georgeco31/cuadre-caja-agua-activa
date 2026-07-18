import {
  CashSaleForm,
  type CreditSaleFormProps,
} from "@/components/CashSaleForm";

type Props = Omit<CreditSaleFormProps, "mode">;

export function CreditSaleForm(props: Props) {
  return <CashSaleForm {...props} mode="credit" />;
}
