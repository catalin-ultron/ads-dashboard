"""Good-execution guarantee retained from payments (D38.02).

retention per situație = min(planned share × certified value, target − balance)
target = target share × contract price excl. VAT, re-based on each value addendum
release: 70% at reception on completion (no claims), 30% at final reception.
Rules per Legea 98/2016 art. 154 and HG 395/2016 art. 39-42 as recorded in 02-coverage.md
(article numbering after HG 336/2023 to verify).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

from nsa.platform.core.money import D, round_money

MAX_TARGET_SHARE = Decimal("0.10")
MIN_INITIAL_DEPOSIT_SHARE = Decimal("0.005")
COMPLETION_RELEASE_SHARE = Decimal("0.70")


class EntryKind(str, Enum):
    INITIAL_DEPOSIT = "initial_deposit"
    RETENTION = "retention"
    RELEASE_COMPLETION = "release_completion"
    RELEASE_FINAL = "release_final"
    CALL = "call"
    RESTORATION = "restoration"


@dataclass(frozen=True)
class Entry:
    kind: EntryKind
    amount: Decimal  # positive increases the held balance, negative decreases it
    reference: str = ""


class GuaranteeError(ValueError):
    pass


@dataclass
class RetentionAccount:
    contract_price: Decimal        # excl. VAT
    target_share: Decimal          # ≤ 10%
    planned_retention_share: Decimal
    entries: list[Entry] = field(default_factory=list)
    completion_released: bool = False
    final_released: bool = False

    def __post_init__(self):
        if not Decimal(0) < D(self.target_share) <= MAX_TARGET_SHARE:
            raise GuaranteeError("Good-execution guarantee must be above 0 and at most 10% of the price")
        if not Decimal(0) < D(self.planned_retention_share) <= Decimal(1):
            raise GuaranteeError("Planned retention share must be a positive fraction")

    @property
    def target(self) -> Decimal:
        return round_money(D(self.contract_price) * D(self.target_share))

    @property
    def balance(self) -> Decimal:
        return sum((e.amount for e in self.entries), Decimal("0"))

    @property
    def outstanding(self) -> Decimal:
        return max(self.target - self.balance, Decimal("0"))

    def deposit_initial(self, amount: Decimal, reference: str = "") -> Entry:
        amount = round_money(amount)
        minimum = round_money(D(self.contract_price) * MIN_INITIAL_DEPOSIT_SHARE)
        if amount < minimum:
            raise GuaranteeError(f"Initial deposit must be at least 0.5% of the price ({minimum})")
        return self._add(Entry(EntryKind.INITIAL_DEPOSIT, min(amount, self.outstanding), reference))

    def retain(self, certified_value: Decimal, reference: str = "") -> Decimal:
        """Retention to deduct from one certified situație."""
        self._require_open()
        amount = min(round_money(D(certified_value) * D(self.planned_retention_share)), self.outstanding)
        if amount > 0:
            self._add(Entry(EntryKind.RETENTION, amount, reference))
        return amount

    def rebase(self, new_contract_price: Decimal) -> None:
        """Value addendum: target follows the new price; balance above target is not refunded early."""
        self.contract_price = D(new_contract_price)

    def call(self, amount: Decimal, reference: str = "") -> Entry:
        amount = round_money(amount)
        if amount <= 0 or amount > self.balance:
            raise GuaranteeError("Called amount must be positive and not exceed the held balance")
        return self._add(Entry(EntryKind.CALL, -amount, reference))

    def restore(self, amount: Decimal, reference: str = "") -> Entry:
        return self._add(Entry(EntryKind.RESTORATION, min(round_money(amount), self.outstanding), reference))

    def release_on_completion(self, claims_pending: bool, reference: str = "") -> Decimal:
        self._require_open()
        if self.completion_released:
            raise GuaranteeError("Completion release already made")
        if claims_pending:
            raise GuaranteeError("Release blocked: claims notified against the guarantee")
        amount = round_money(self.balance * COMPLETION_RELEASE_SHARE)
        self._add(Entry(EntryKind.RELEASE_COMPLETION, -amount, reference))
        self.completion_released = True
        return amount

    def release_final(self, claims_pending: bool, reference: str = "") -> Decimal:
        if not self.completion_released:
            raise GuaranteeError("Final release requires the completion release first")
        if self.final_released:
            raise GuaranteeError("Final release already made")
        if claims_pending:
            raise GuaranteeError("Release blocked: claims notified against the guarantee")
        amount = self.balance
        self._add(Entry(EntryKind.RELEASE_FINAL, -amount, reference))
        self.final_released = True
        return amount

    def _require_open(self):
        if self.completion_released:
            raise GuaranteeError("No further retention after the completion release")

    def _add(self, entry: Entry) -> Entry:
        self.entries.append(entry)
        return entry
