from sqlalchemy.orm import Session

from app.models.network_operator import NetworkOperator
from app.models.network_operator_coverage import NetworkOperatorCoverage
from app.models.postal_code import PostalCode


def resolve_network_operator(
    db: Session,
    *,
    postal_code: PostalCode,
    street_code: str | None = None,
) -> NetworkOperator | None:
    """
    Resolve the network operator for an address.

    Coverage rules are preferred over the legacy
    PostalCode.network_operator_id mapping.

    More specific rules win:
    street > PLZ/Ort > GKZ.

    priority is used as an additional ordering criterion.
    """

    if postal_code.gkz:
        rules = (
            db.query(NetworkOperatorCoverage)
            .filter(
                NetworkOperatorCoverage.active.is_(True),
                NetworkOperatorCoverage.gkz == postal_code.gkz,
            )
            .all()
        )

        matching_rules = []

        for rule in rules:
            if (
                rule.postal_code is not None
                and rule.postal_code != postal_code.postal_code
            ):
                continue

            if (
                rule.city is not None
                and rule.city != postal_code.city
            ):
                continue

            if rule.street_code is not None:
                if street_code is None:
                    continue

                if rule.street_code != street_code:
                    continue

            specificity = 0

            if rule.postal_code is not None:
                specificity += 10

            if rule.city is not None:
                specificity += 10

            if rule.street_code is not None:
                specificity += 100

            matching_rules.append(
                (
                    specificity,
                    rule.priority,
                    rule.id,
                    rule,
                )
            )

        if matching_rules:
            # Only resolve automatically when the best matching
            # coverage level identifies exactly one network operator.
            best_specificity = max(
                item[0] for item in matching_rules
            )

            most_specific_rules = [
                item
                for item in matching_rules
                if item[0] == best_specificity
            ]

            best_priority = max(
                item[1] for item in most_specific_rules
            )

            best_rules = [
                item[3]
                for item in most_specific_rules
                if item[1] == best_priority
            ]

            operator_ids = {
                rule.network_operator_id
                for rule in best_rules
            }

            if len(operator_ids) == 1:
                operator_id = next(iter(operator_ids))

                return (
                    db.query(NetworkOperator)
                    .filter(
                        NetworkOperator.id == operator_id
                    )
                    .first()
                )

            # More than one equally valid operator:
            # the address is ambiguous and must not be guessed.
            return None

    # Legacy fallback while coverage data is being introduced.
    if postal_code.network_operator_id is not None:
        return (
            db.query(NetworkOperator)
            .filter(
                NetworkOperator.id
                == postal_code.network_operator_id
            )
            .first()
        )

    return None
