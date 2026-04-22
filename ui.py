import logging
import tkinter as tk
from tkinter import messagebox, ttk

from bot.logging_config import setup_logging
from bot.orders import OrderService
from bot.validators import validate_order_request


class TradingBotUI:
    def __init__(self) -> None:
        self.log_path = setup_logging()
        self.logger = logging.getLogger(__name__)
        self.root = tk.Tk()
        self.root.title("Binance Futures Testnet Bot")
        self.root.geometry("520x520")
        self.root.resizable(False, False)

        self.symbol_var = tk.StringVar(value="BTCUSDT")
        self.side_var = tk.StringVar(value="BUY")
        self.type_var = tk.StringVar(value="MARKET")
        self.quantity_var = tk.StringVar(value="0.001")
        self.price_var = tk.StringVar()
        self.stop_price_var = tk.StringVar()

        self._build_layout()
        self._toggle_fields()

    def _build_layout(self) -> None:
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Binance Futures Testnet Order", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 16)
        )

        fields = [
            ("Symbol", self.symbol_var),
            ("Quantity", self.quantity_var),
            ("Price", self.price_var),
            ("Stop Price", self.stop_price_var),
        ]

        ttk.Label(frame, text="Side").grid(row=1, column=0, sticky="w", pady=6)
        side_combo = ttk.Combobox(frame, textvariable=self.side_var, values=["BUY", "SELL"], state="readonly")
        side_combo.grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Order Type").grid(row=2, column=0, sticky="w", pady=6)
        type_combo = ttk.Combobox(
            frame,
            textvariable=self.type_var,
            values=["MARKET", "LIMIT", "STOP_LIMIT"],
            state="readonly",
        )
        type_combo.grid(row=2, column=1, sticky="ew", pady=6)
        type_combo.bind("<<ComboboxSelected>>", lambda _event: self._toggle_fields())

        self.entry_widgets = {}
        row = 3
        for label, variable in fields:
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=6)
            entry = ttk.Entry(frame, textvariable=variable)
            entry.grid(row=row, column=1, sticky="ew", pady=6)
            self.entry_widgets[label] = entry
            row += 1

        ttk.Button(frame, text="Place Order", command=self.submit_order).grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=(16, 10)
        )
        row += 1

        ttk.Label(frame, text="Response").grid(row=row, column=0, columnspan=2, sticky="w")
        row += 1

        self.output = tk.Text(frame, height=12, width=58, state="disabled", wrap="word")
        self.output.grid(row=row, column=0, columnspan=2, sticky="nsew", pady=(6, 0))

        frame.columnconfigure(1, weight=1)

    def _toggle_fields(self) -> None:
        order_type = self.type_var.get()
        price_state = "normal" if order_type in {"LIMIT", "STOP_LIMIT"} else "disabled"
        stop_state = "normal" if order_type == "STOP_LIMIT" else "disabled"

        self.entry_widgets["Price"].configure(state=price_state)
        self.entry_widgets["Stop Price"].configure(state=stop_state)

        if price_state == "disabled":
            self.price_var.set("")
        if stop_state == "disabled":
            self.stop_price_var.set("")

    def submit_order(self) -> None:
        try:
            order_request = validate_order_request(
                symbol=self.symbol_var.get(),
                side=self.side_var.get(),
                order_type=self.type_var.get(),
                quantity=self.quantity_var.get(),
                price=self.price_var.get() or None,
                stop_price=self.stop_price_var.get() or None,
            )

            response = OrderService().create_order(
                symbol=order_request["symbol"],
                side=order_request["side"],
                order_type=order_request["type"],
                quantity=order_request["quantity"],
                price=order_request["price"],
                stop_price=order_request["stop_price"],
            )

            lines = [
                "Order placed successfully",
                f"Order ID: {response.get('orderId', 'N/A')}",
                f"Status: {response.get('status', 'N/A')}",
                f"Executed Qty: {response.get('executedQty', 'N/A')}",
                f"Avg Price: {response.get('avgPrice') or 'N/A'}",
            ]
            self._write_output("\n".join(lines))
        except Exception as exc:
            self.logger.exception("UI order submission failed")
            self._write_output(f"FAILED: {exc}\nLog file: {self.log_path}")
            messagebox.showerror("Order Failed", str(exc))

    def _write_output(self, message: str) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, message)
        self.output.configure(state="disabled")

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    TradingBotUI().run()
