import { useEffect, useState } from 'react'

function NewContract() {
    const [energyType, setEnergyType] = useState('strom')
    const [customerType, setCustomerType] = useState('privat')
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

    const [networkOperatorIdentifiers, setNetworkOperatorIdentifiers] = useState([])
    const [networkOperatorOptions, setNetworkOperatorOptions] = useState([])
    const [selectedBundesland, setSelectedBundesland] = useState('')
    const [selectedNetworkOperator, setSelectedNetworkOperator] = useState(null)
    const [networkOperatorSource, setNetworkOperatorSource] = useState('')
    const [showAllNetworkOperators, setShowAllNetworkOperators] = useState(false)
    const [zpn, setZpn] = useState('')
    const [networkOperatorLoading, setNetworkOperatorLoading] = useState(false)
    const [networkOperatorError, setNetworkOperatorError] = useState('')

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

    const getBundeslandFromGkz = (gkz) => {
        const firstDigit = String(gkz || '').trim().charAt(0)

        const bundeslandByGkz = {
            1: 'Burgenland',
            2: 'Kärnten',
            3: 'Niederösterreich',
            4: 'Oberösterreich',
            5: 'Salzburg',
            6: 'Steiermark',
            7: 'Tirol',
            8: 'Vorarlberg',
            9: 'Wien',
        }

        return bundeslandByGkz[firstDigit] || ''
    }

    useEffect(() => {
        const controller = new AbortController()

        const loadNetworkOperators = async () => {
            try {
                setNetworkOperatorLoading(true)
                setNetworkOperatorError('')

                const token = localStorage.getItem('access_token')

                const response = await fetch(
                    `http://127.0.0.1:8000/network-operator-identifiers?energy_type=${encodeURIComponent(energyType)}`,
                    {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                        signal: controller.signal,
                    }
                )

                if (!response.ok) {
                    throw new Error('Netzbetreiber konnten nicht geladen werden.')
                }

                const data = await response.json()
                setNetworkOperatorIdentifiers(data)
            } catch (error) {
                if (error.name !== 'AbortError') {
                    console.error(error)
                    setNetworkOperatorIdentifiers([])
                    setNetworkOperatorError(
                        'Netzbetreiber konnten nicht geladen werden.'
                    )
                }
            } finally {
                setNetworkOperatorLoading(false)
            }
        }

        setSelectedBundesland('')
        setNetworkOperatorOptions([])
        setSelectedNetworkOperator(null)
        setNetworkOperatorSource('')
        setShowAllNetworkOperators(false)
        setZpn('')
        loadNetworkOperators()

        return () => controller.abort()
    }, [energyType])

    const bundeslaender = [
        ...new Set(
            networkOperatorIdentifiers
                .map((item) => item.bundesland)
                .filter(Boolean)
        ),
    ].sort((a, b) => a.localeCompare(b, 'de'))

    useEffect(() => {
        if (!selectedBundesland) {
            setNetworkOperatorOptions([])
            return
        }

        const controller = new AbortController()

        const loadNetworkOperatorOptions = async () => {
            try {
                setNetworkOperatorLoading(true)
                setNetworkOperatorError('')

                const token = localStorage.getItem('access_token')

                const params = new URLSearchParams({
                    energy_type: energyType,
                    bundesland: selectedBundesland,
                })

                const response = await fetch(
                    `http://127.0.0.1:8000/network-operator-identifiers?${params.toString()}`,
                    {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                        signal: controller.signal,
                    }
                )

                if (!response.ok) {
                    throw new Error(
                        'Netzbetreiber konnten nicht geladen werden.'
                    )
                }

                const data = await response.json()
                setNetworkOperatorOptions(data)
            } catch (error) {
                if (error.name !== 'AbortError') {
                    console.error(error)
                    setNetworkOperatorOptions([])
                    setNetworkOperatorError(
                        'Netzbetreiber konnten nicht geladen werden.'
                    )
                }
            } finally {
                setNetworkOperatorLoading(false)
            }
        }

        setShowAllNetworkOperators(false)
        loadNetworkOperatorOptions()

        return () => controller.abort()
    }, [energyType, selectedBundesland])

    const filteredNetworkOperators = networkOperatorOptions

    const preferredNetworkOperators = filteredNetworkOperators.filter(
        (item) => item.standard_visible === true
    )

    const baseVisibleNetworkOperators = showAllNetworkOperators
        ? filteredNetworkOperators
        : preferredNetworkOperators

    const visibleNetworkOperators =
        selectedNetworkOperator &&
        !baseVisibleNetworkOperators.some(
            (item) =>
                item.network_operator_id ===
                    selectedNetworkOperator.network_operator_id &&
                item.zpn_prefix === selectedNetworkOperator.zpn_prefix
        )
            ? [selectedNetworkOperator, ...baseVisibleNetworkOperators]
            : baseVisibleNetworkOperators

    useEffect(() => {
        if (
            !selectedPostalCode ||
            zpn.trim() ||
            networkOperatorIdentifiers.length === 0 ||
            networkOperatorSource === 'manual'
        ) {
            return
        }

        const controller = new AbortController()

        const resolveAddressNetworkOperator = async () => {
            try {
                setNetworkOperatorLoading(true)
                setNetworkOperatorError('')

                const token = localStorage.getItem('access_token')

                const params = new URLSearchParams({
                    postal_code_id: String(selectedPostalCode.id),
                })

                if (selectedStreet?.street_code) {
                    params.set(
                        'street_code',
                        String(selectedStreet.street_code)
                    )
                }

                const response = await fetch(
                    `http://127.0.0.1:8000/network-operators/resolve-by-address?${params.toString()}`,
                    {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                        signal: controller.signal,
                    }
                )

                if (!response.ok) {
                    const data = await response.json()
                    throw new Error(
                        data.detail ||
                        'Netzbetreiber konnte nicht automatisch ermittelt werden.'
                    )
                }

                const data = await response.json()

                if (!data) {
                    setSelectedNetworkOperator(null)
                    setNetworkOperatorSource('')
                    setShowAllNetworkOperators(false)
                    return
                }

                const identifier = networkOperatorIdentifiers.find(
                    (item) =>
                        item.network_operator_id === data.id &&
                        item.energy_type.toLowerCase() ===
                            energyType.toLowerCase()
                )

                if (!identifier) {
                    throw new Error(
                        'Der Netzbetreiber wurde gefunden, aber es fehlt das AT-Präfix.'
                    )
                }

                setSelectedNetworkOperator(identifier)
                setNetworkOperatorSource('address')
                setShowAllNetworkOperators(false)
            } catch (error) {
                if (error.name !== 'AbortError') {
                    console.error(error)
                    setSelectedNetworkOperator(null)
                    setNetworkOperatorSource('')
                    setNetworkOperatorError(
                        error.message ||
                        'Netzbetreiber konnte nicht automatisch ermittelt werden.'
                    )
                }
            } finally {
                setNetworkOperatorLoading(false)
            }
        }

        resolveAddressNetworkOperator()

        return () => controller.abort()
    }, [
        selectedPostalCode,
        selectedStreet,
        energyType,
        networkOperatorIdentifiers,
        zpn,
        networkOperatorSource,
    ])

    const resolveZpn = async (value) => {
        const normalized = value.replace(/\s+/g, '').toUpperCase()

        setZpn(value)
        setSelectedNetworkOperator(null)
        setNetworkOperatorSource('')
        setNetworkOperatorError('')
        setCalculationResult(null)
        setCalculationError('')

        if (normalized.length < 8) {
            return
        }

        try {
            setNetworkOperatorLoading(true)

            const token = localStorage.getItem('access_token')

            const response = await fetch(
                `http://127.0.0.1:8000/network-operator-identifiers/resolve?energy_type=${encodeURIComponent(energyType)}&zpn=${encodeURIComponent(normalized)}`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            )

            const data = await response.json()

            if (!response.ok) {
                throw new Error(
                    data.detail || 'Kein Netzbetreiber für diese Zählpunktnummer gefunden.'
                )
            }

            setSelectedNetworkOperator(data)
            setNetworkOperatorSource('zpn')
            setShowAllNetworkOperators(false)
        } catch (error) {
            console.error(error)
            setNetworkOperatorError(
                error.message ||
                'Kein Netzbetreiber für diese Zählpunktnummer gefunden.'
            )
        } finally {
            setNetworkOperatorLoading(false)
        }
    }

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

        if (!selectedNetworkOperator) {
            setCalculationError(
                'Bitte wählen Sie einen Netzbetreiber oder geben Sie die Zählpunktnummer ein.'
            )
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
                        street_code: selectedStreet?.street_code ?? null,
                        network_operator_id: selectedNetworkOperator.network_operator_id,
                        consumption_kwh: consumptionValue,
                        customer_type: customerType,
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
                    <div className="form-section">
                        <label className="form-label">Kundentyp</label>

                        <div className="energy-type-buttons">
                            <button
                                type="button"
                                className={`energy-type-button ${customerType === 'privat' ? 'active' : ''
                                    }`}
                                onClick={() => {
                                    setCustomerType('privat')
                                    setCalculationResult(null)
                                    setCalculationError('')
                                }}
                            >
                                <svg
                                    className="customer-type-icon"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    aria-hidden="true"
                                >
                                    <path d="M3 10.8 12 3l9 7.8" />
                                    <path d="M5.5 9.5V21h13V9.5" />
                                    <path d="M9.5 21v-6h5v6" />
                                </svg>
                                Privatkunde
                            </button>

                            <button
                                type="button"
                                className={`energy-type-button ${customerType === 'gewerbe' ? 'active' : ''
                                    }`}
                                onClick={() => {
                                    setCustomerType('gewerbe')
                                    setCalculationResult(null)
                                    setCalculationError('')
                                }}
                            >
                                <svg
                                    className="customer-type-icon"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    aria-hidden="true"
                                >
                                    <path d="M4 21V5h11v16" />
                                    <path d="M15 9h5v12" />
                                    <path d="M8 9h3M8 13h3M8 17h3M17 13h1M17 17h1" />
                                </svg>
                                Gewerbekunde
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
                                    setSelectedBundesland('')
                                    setSelectedNetworkOperator(null)
                                    setNetworkOperatorSource('')
                                    setShowAllNetworkOperators(false)
                                    setZpn('')
                                    setNetworkOperatorError('')
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
                                                setSelectedBundesland(
                                                    getBundeslandFromGkz(option.gkz)
                                                )
                                                setSelectedNetworkOperator(null)
                                                setNetworkOperatorSource('')
                                                setShowAllNetworkOperators(false)
                                                setZpn('')
                                                setNetworkOperatorError('')
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
                        <label className="form-label">Netzbetreiber</label>

                        <div className="tariff-form-grid">
                            <div className="form-field">
                                <label htmlFor="bundesland">
                                    Bundesland
                                </label>

                                <select
                                    id="bundesland"
                                    value={selectedBundesland}
                                    disabled={Boolean(selectedPostalCode)}
                                    onChange={(event) => {
                                        setSelectedBundesland(event.target.value)
                                        setSelectedNetworkOperator(null)
                                        setZpn('')
                                        setNetworkOperatorError('')
                                        setCalculationResult(null)
                                        setCalculationError('')
                                    }}
                                >
                                    <option value="">
                                        Bundesland auswählen
                                    </option>

                                    {bundeslaender.map((bundesland) => (
                                        <option
                                            key={bundesland}
                                            value={bundesland}
                                        >
                                            {bundesland}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="form-field">
                                <label htmlFor="networkOperator">
                                    Netzbetreiber
                                </label>

                                <select
                                    id="networkOperator"
                                    disabled={!selectedBundesland}
                                    value={
                                        selectedNetworkOperator
                                            ? `${selectedNetworkOperator.energy_type}:${selectedNetworkOperator.zpn_prefix}`
                                            : ''
                                    }
                                    onChange={(event) => {
                                        if (event.target.value === '__more__') {
                                            setShowAllNetworkOperators(true)
                                            setSelectedNetworkOperator(null)
                                            setNetworkOperatorSource('')
                                            setNetworkOperatorError('')
                                            return
                                        }

                                        const selected = filteredNetworkOperators.find(
                                            (item) =>
                                                `${item.energy_type}:${item.zpn_prefix}` ===
                                                event.target.value
                                        )

                                        setSelectedNetworkOperator(selected || null)
                                        setNetworkOperatorSource(
                                            selected ? 'manual' : ''
                                        )
                                        setZpn('')
                                        setNetworkOperatorError('')
                                        setCalculationResult(null)
                                        setCalculationError('')
                                    }}
                                >
                                    <option value="">
                                        {selectedBundesland
                                            ? 'Netzbetreiber auswählen'
                                            : 'Zuerst Bundesland auswählen'}
                                    </option>

                                    {visibleNetworkOperators.map((item) => (
                                        <option
                                            key={`${item.energy_type}:${item.zpn_prefix}`}
                                            value={`${item.energy_type}:${item.zpn_prefix}`}
                                        >
                                            {item.network_operator_name} — {item.zpn_prefix}
                                        </option>
                                    ))}

                                    {!showAllNetworkOperators &&
                                        filteredNetworkOperators.length >
                                            preferredNetworkOperators.length && (
                                            <option value="__more__">
                                                Weitere Netzbetreiber …
                                            </option>
                                        )}
                                </select>
                            </div>
                        </div>

                        <div className="form-field" style={{ marginTop: '16px' }}>
                            <label htmlFor="zpn">
                                Zählpunktnummer / erste 8 Zeichen
                            </label>

                            <input
                                id="zpn"
                                type="text"
                                placeholder="z. B. AT001000"
                                autoComplete="off"
                                value={zpn}
                                onChange={(event) => resolveZpn(event.target.value)}
                            />

                            {networkOperatorLoading && (
                                <div className="postal-search-status">
                                    Netzbetreiber wird gesucht...
                                </div>
                            )}

                            {selectedNetworkOperator && (
                                <div
                                    style={{
                                        marginTop: '10px',
                                        fontSize: '14px',
                                        fontWeight: 600,
                                    }}
                                >
                                    {selectedNetworkOperator.network_operator_name}
                                    {' · '}
                                    {selectedNetworkOperator.zpn_prefix}
                                    {' · '}
                                    {selectedNetworkOperator.bundesland}
                                </div>
                            )}

                            {networkOperatorError && (
                                <div
                                    style={{
                                        marginTop: '10px',
                                        color: '#a12626',
                                        fontSize: '14px',
                                    }}
                                >
                                    {networkOperatorError}
                                </div>
                            )}
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