import {
  CashSaleList,
  type CashSaleListProps,
} from "@/components/CashSaleList";

type Props = Omit<CashSaleListProps, "mode">;

export function CreditSaleList(props: Props) {
  return <CashSaleList {...props} mode="credit" />;
}
