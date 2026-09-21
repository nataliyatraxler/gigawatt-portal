import { useEffect, useState } from 'react'

function NewContract() {
    const [energyType, setEnergyType] = useState('strom')
    const [postalCode, setPostalCode] = useState('')
    const [consumption, setConsumption] = useState('3500')
    const [persons, setPersons] = useState(2)

    const [postalOptions, setPostalOptions] = useState([])
    const [selectedPostalCode, setSelectedPostalCode] = useState(null)
    const [postalLoading, setPostalLoading] = useState(false)

    const [street, setStreet] = useState('')
    const [streetOptions, setStreetOptions] = useState([])
    const [selectedStreet, setSelectedStreet] = useState(null)
    const [streetLoading, setStreetLoading] = useState(false)

    const [houseNumber, setHouseNumber] = useState('')

    const [calculationResult, setCalculationResult] = useState(null)
    const [calculationLoading, setCalculationLoading] = useState(false)
    const [calculationError, setCalculationError] = useState('')

    useEffect(() => {
        const query = postalCode.trim()

        if (query.length < 2 || selectedPostalCode) {
            setPostalOptions([])
            return
        }

        const controller = new AbortController()

        const timer = setTimeout(async () => {
            try {
                setPostalLoading(true)

                const token = localStorage.getItem('access_token')

                const response = await fetch(
                    `http://127.0.0.1:8000/postal-codes/search?q=${encodeURIComponent(query)}`,
                    {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                        signal: controller.signal,
                    }
                )

                if (!response.ok) {
                    throw new Error('PLZ-Suche fehlgeschlagen')
                }

                const data = await response.json()
                setPostalOptions(data)
            } catch (error) {
                if (error.name !== 'AbortError') {
                    console.error(error)
                    setPostalOptions([])
                }
            } finally {
                setPostalLoading(false)
            }
        }, 300)

        return () => {
            clearTimeout(timer)
            controller.abort()
        }
    }, [postalCode, selectedPostalCode])

    useEffect(() => {
        if (!selectedPostalCode) {
            setStreetOptions([])
            return
        }

        const controller = new AbortController()

        const loadStreets = async () => {
            try {
                setStreetLoading(true)

                const token = localStorage.getItem('access_token')

                const response = await fetch(
                    `http://127.0.0.1:8000/postal-codes/${selectedPostalCode.id}/streets`,
                    {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                        signal: controller.signal,
                    }
                )

                if (!response.ok) {
                    throw new Error('Straßensuche fehlgeschlagen')
                }

                const data = await response.json()
                setStreetOptions(data)
            } catch (error) {
                if (error.name !== 'AbortError') {
                    console.error(error)
                    setStreetOptions([])
                }
            } finally {
                setStreetLoading(false)
            }
        }

        loadStreets()

        return () => controller.abort()
    }, [selectedPostalCode])

    const getLocalDate = () => {
        const now = new Date()

        const year = now.getFullYear()
        const month = String(now.getMonth() + 1).padStart(2, '0')
        const day = String(now.getDate()).padStart(2, '0')

        return `${year}-${month}-${day}`
    }

    const formatEuro = (value) => {
        return Number(value).toLocaleString('de-AT', {
            style: 'currency',
            currency: 'EUR',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        })
    }

    const handleSubmit = async (event) => {
        event.preventDefault()

        setCalculationError('')
        setCalculationResult(null)

        if (energyType !== 'strom') {
            setCalculationError(
                'Die Netzkostenberechnung für Gas ist derzeit noch nicht verfügbar.'
            )
            return
        }

        if (!selectedPostalCode) {
            setCalculationError('Bitte wählen Sie eine Postleitzahl und einen Ort aus.')
            return
        }

        if (!selectedStreet) {
            setCalculationError('Bitte wählen Sie eine Straße aus.')
            return
        }

        if (!houseNumber.trim()) {
            setCalculationError('Bitte geben Sie eine Hausnummer ein.')
            return
        }

        const consumptionValue = Number(consumption)

        if (!Number.isFinite(consumptionValue) || consumptionValue <= 0) {
            setCalculationError('Bitte geben Sie einen gültigen Jahresverbrauch ein.')
            return
        }

        try {
            setCalculationLoading(true)

            const token = localStorage.getItem('access_token')

            const response = await fetch(
                'http://127.0.0.1:8000/calculator/network-costs',
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: `Bearer ${token}`,
                    },
                    body: JSON.stringify({
                        postal_code_id: selectedPostalCode.id,
                        consumption_kwh: consumptionValue,
                        calculation_date: getLocalDate(),
                        network_level: 7,
                        tariff_type: 'nicht_gemessen',
                        meter_type: 'standard',
                    }),
                }
            )

            const data = await response.json()

            if (!response.ok) {
                throw new Error(
                    data.detail || 'Die Netzkosten konnten nicht berechnet werden.'
                )
            }

            setCalculationResult(data)
        } catch (error) {
            console.error(error)

            setCalculationError(
                error.message ||
                'Die Netzkosten konnten nicht berechnet werden.'
            )
        } finally {
            setCalculationLoading(false)
        }
    }

    return (
        <div className="page-content new-contract-page">
            <div className="page-header">
                <div>
                    <h1>Neuer Vertrag</h1>
                    <p>Tarif berechnen und neuen Vertrag erstellen.</p>
                </div>
            </div>

            <div className="tariff-calculator-card">
                <div className="tariff-calculator-header">
                    <div className="tariff-calculator-icon">⚡</div>

                    <div>
                        <h2>Tarifrechner</h2>
                        <p>
                            Finden Sie den passenden Energie-Tarif für Ihren Kunden.
                        </p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="tariff-form">
                    <div className="form-section">
                        <label className="form-label">Energieart</label>

                        <div className="energy-type-buttons">
                            <button
                                type="button"
                                className={`energy-type-button ${energyType === 'strom' ? 'active' : ''
                                    }`}
                                onClick={() => {
                                    setEnergyType('strom')
                                    setCalculationResult(null)
                                    setCalculationError('')
                                }}
                            >
                                <span>⚡</span>
                                Strom
                            </button>

                            <button
                                type="button"
                                className={`energy-type-button ${energyType === 'gas' ? 'active' : ''
                                    }`}
                                onClick={() => {
                                    setEnergyType('gas')
                                    setCalculationResult(null)
                                    setCalculationError('')
                                }}
                            >
                                <span>🔥</span>
                                Gas
                            </button>
                        </div>
                    </div>

                    <div className="tariff-form-grid">
                        <div className="form-field postal-code-field">
                            <label htmlFor="postalCode">
                                Postleitzahl / Ort
                            </label>

                            <input
                                id="postalCode"
                                type="text"
                                placeholder="PLZ oder Ort eingeben"
                                autoComplete="off"
                                value={postalCode}
                                onChange={(event) => {
                                    setPostalCode(event.target.value)
                                    setSelectedPostalCode(null)
                                    setStreet('')
                                    setSelectedStreet(null)
                                    setStreetOptions([])
                                    setHouseNumber('')
                                    setCalculationResult(null)
                                    setCalculationError('')
                                }}
                            />

                            {postalLoading && (
                                <div className="postal-search-status">
                                    Suche...
                                </div>
                            )}

                            {!postalLoading && postalOptions.length > 0 && (
                                <div className="postal-options">
                                    {postalOptions.map((option) => (
                                        <button
                                            key={option.id}
                                            type="button"
                                            className="postal-option"
                                            onClick={() => {
                                                setSelectedPostalCode(option)
                                                setPostalCode(
                                                    `${option.postal_code} ${option.city}`
                                                )
                                                setPostalOptions([])
                                                setStreet('')
                                                setSelectedStreet(null)
                                                setHouseNumber('')
                                                setCalculationResult(null)
                                                setCalculationError('')
                                            }}
                                        >
                                            <strong>{option.postal_code}</strong>
                                            <span>
                                                {option.city}
                                                {option.municipality &&
                                                    option.municipality !== option.city &&
                                                    ` — ${option.municipality}`}
                                            </span>
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>

                        <div className="form-field">
                            <label htmlFor="consumption">
                                Jahresverbrauch
                            </label>

                            <div className="input-with-unit">
                                <input
                                    id="consumption"
                                    type="number"
                                    min="1"
                                    value={consumption}
                                    onChange={(event) => {
                                        setConsumption(event.target.value)
                                        setCalculationResult(null)
                                        setCalculationError('')
                                    }}
                                />

                                <span>kWh</span>
                            </div>
                        </div>
                    </div>

                    <div className="tariff-form-grid">
                        <div className="form-field postal-code-field">
                            <label htmlFor="street">
                                Straße
                            </label>

                            <input
                                id="street"
                                type="text"
                                placeholder={
                                    selectedPostalCode
                                        ? 'Straße auswählen'
                                        : 'Zuerst PLZ / Ort auswählen'
                                }
                                autoComplete="off"
                                disabled={!selectedPostalCode}
                                value={street}
                                onChange={(event) => {
                                    setStreet(event.target.value)
                                    setSelectedStreet(null)
                                    setHouseNumber('')
                                    setCalculationResult(null)
                                    setCalculationError('')
                                }}
                            />

                            {streetLoading && (
                                <div className="postal-search-status">
                                    Straßen werden geladen...
                                </div>
                            )}

                            {!streetLoading &&
                                selectedPostalCode &&
                                !selectedStreet &&
                                streetOptions.length > 0 && (
                                    <div className="postal-options">
                                        {streetOptions
                                            .filter((option) =>
                                                option.name
                                                    .toLowerCase()
                                                    .includes(street.toLowerCase())
                                            )
                                            .map((option) => (
                                                <button
                                                    key={option.street_code}
                                                    type="button"
                                                    className="postal-option"
                                                    onClick={() => {
                                                        setSelectedStreet(option)
                                                        setStreet(option.name)
                                                        setHouseNumber('')
                                                        setCalculationResult(null)
                                                        setCalculationError('')
                                                    }}
                                                >
                                                    <span>{option.name}</span>
                                                </button>
                                            ))}
                                    </div>
                                )}
                        </div>

                        <div className="form-field">
                            <label htmlFor="houseNumber">
                                Hausnummer
                            </label>

                            <input
                                id="houseNumber"
                                type="text"
                                placeholder="z. B. 12"
                                value={houseNumber}
                                disabled={!selectedStreet}
                                onChange={(event) => {
                                    setHouseNumber(event.target.value)
                                    setCalculationResult(null)
                                    setCalculationError('')
                                }}
                            />
                        </div>
                    </div>

                    <div className="form-section">
                        <label className="form-label">
                            Personen im Haushalt
                        </label>

                        <div className="persons-buttons">
                            {[1, 2, 3, 4].map((number) => (
                                <button
                                    key={number}
                                    type="button"
                                    className={`person-button ${persons === number ? 'active' : ''
                                        }`}
                                    onClick={() => setPersons(number)}
                                >
                                    {number === 4 ? '4+' : number}
                                </button>
                            ))}
                        </div>
                    </div>

                    {calculationError && (
                        <div
                            style={{
                                padding: '14px 16px',
                                borderRadius: '10px',
                                background: '#fff3f3',
                                color: '#a12626',
                                marginBottom: '18px',
                            }}
                        >
                            {calculationError}
                        </div>
                    )}

                    <div className="tariff-form-footer">
                        <div className="tariff-info">
                            <span>✓</span>
                            Kostenloser Tarifvergleich
                        </div>

                        <button
                            type="submit"
                            className="tariff-submit-button"
                            disabled={calculationLoading}
                        >
                            {calculationLoading
                                ? 'Tarife werden berechnet...'
                                : 'Tarife vergleichen'}
                            <span>→</span>
                        </button>
                    </div>
                </form>
            </div>

            {calculationResult && (
                <div
                    className="tariff-calculator-card"
                    style={{ marginTop: '24px' }}
                >
                    <div className="tariff-calculator-header">
                        <div className="tariff-calculator-icon">€</div>

                        <div>
                            <h2>Netzkosten</h2>
                            <p>
                                {calculationResult.address.postal_code}{' '}
                                {calculationResult.address.city}
                                {' · '}
                                {calculationResult.network_operator.name}
                            </p>
                        </div>
                    </div>

                    <div className="tariff-form">
                        <div className="tariff-form-grid">
                            <div className="form-field">
                                <label>Netznutzungsentgelt</label>
                                <strong>
                                    {formatEuro(
                                        calculationResult.network.base_price +
                                        calculationResult.network.work_price
                                    )}
                                </strong>
                            </div>

                            <div className="form-field">
                                <label>Netzverlustentgelt</label>
                                <strong>
                                    {formatEuro(
                                        calculationResult.network.network_loss
                                    )}
                                </strong>
                            </div>

                            <div className="form-field">
                                <label>Messentgelt</label>
                                <strong>
                                    {formatEuro(
                                        calculationResult.network.metering_cost
                                    )}
                                </strong>
                            </div>

                            <div className="form-field">
                                <label>Netztarif</label>
                                <strong>
                                    {formatEuro(
                                        calculationResult.network
                                            .total_network_tariff
                                    )}
                                </strong>
                            </div>
                        </div>

                        <div
                            style={{
                                borderTop: '1px solid #e7e7e7',
                                margin: '24px 0',
                            }}
                        />

                        <div className="tariff-form-grid">
                            <div className="form-field">
                                <label>Elektrizitätsabgabe</label>
                                <strong>
                                    {formatEuro(
                                        calculationResult.charges
                                            .electricity_tax
                                    )}
                                </strong>
                            </div>

                            <div className="form-field">
                                <label>Erneuerbaren-Förderbeitrag</label>
                                <strong>
                                    {formatEuro(
                                        calculationResult.charges
                                            .renewable_contribution
                                    )}
                                </strong>
                            </div>

                            <div className="form-field">
                                <label>Erneuerbaren-Förderpauschale</label>
                                <strong>
                                    {formatEuro(
                                        calculationResult.charges
                                            .renewable_flat_fee
                                    )}
                                </strong>
                            </div>

                            <div className="form-field">
                                <label>Gebrauchsabgabe</label>
                                <strong>
                                    {formatEuro(
                                        calculationResult.charges.usage_fee
                                    )}
                                </strong>
                            </div>
                        </div>

                        <div
                            style={{
                                borderTop: '1px solid #e7e7e7',
                                margin: '24px 0',
                            }}
                        />

                        <div className="tariff-form-grid">
                            <div className="form-field">
                                <label>Netzkosten exkl. USt.</label>
                                <strong>
                                    {formatEuro(
                                        calculationResult.net_total
                                    )}
                                </strong>
                            </div>

                            <div className="form-field">
                                <label>
                                    Umsatzsteuer{' '}
                                    {calculationResult.vat_percent} %
                                </label>
                                <strong>
                                    {formatEuro(calculationResult.vat)}
                                </strong>
                            </div>
                        </div>

                        <div
                            style={{
                                marginTop: '24px',
                                padding: '22px',
                                borderRadius: '12px',
                                background: '#f4f7f6',
                            }}
                        >
                            <div
                                style={{
                                    fontSize: '14px',
                                    marginBottom: '6px',
                                }}
                            >
                                Netzkosten inkl. Umsatzsteuer
                            </div>

                            <strong
                                style={{
                                    fontSize: '30px',
                                }}
                            >
                                {formatEuro(
                                    calculationResult.gross_total
                                )}
                            </strong>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default NewContract