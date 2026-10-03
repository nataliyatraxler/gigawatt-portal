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
    const [tariffResults, setTariffResults] = useState([])
    const [selectedTariffResult, setSelectedTariffResult] = useState(null)
    const [commissionVisible, setCommissionVisible] = useState(false)
    const [commissionData, setCommissionData] = useState(null)
    const [commissionLoading, setCommissionLoading] = useState(false)
    const [commissionError, setCommissionError] = useState('')
    const [networkDetailsOpen, setNetworkDetailsOpen] = useState(false)
    const [tariffDocumentsOpen, setTariffDocumentsOpen] = useState(false)
    const [tariffDocuments, setTariffDocuments] = useState([])
    const [tariffDocumentsLoading, setTariffDocumentsLoading] = useState(false)
    const [tariffDocumentsError, setTariffDocumentsError] = useState('')

    async function toggleTariffCommission() {
        if (commissionVisible) {
            setCommissionVisible(false)
            return
        }

        setCommissionVisible(true)

        if (commissionData) {
            return
        }

        setCommissionLoading(true)
        setCommissionError('')

        try {
            const token = localStorage.getItem('access_token')
            const calculationDate = getLocalDate()

            const response = await fetch(
                `http://127.0.0.1:8000/calculator/tariffs/${selectedTariffResult.tariff_id}/commission?calculation_date=${encodeURIComponent(calculationDate)}`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            )

            const data = await response.json()

            if (!response.ok) {
                throw new Error(
                    data.detail || 'Provision konnte nicht geladen werden.'
                )
            }

            setCommissionData(data)
        } catch (error) {
            setCommissionData(null)
            setCommissionError(
                error.message || 'Provision konnte nicht geladen werden.'
            )
        } finally {
            setCommissionLoading(false)
        }
    }
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
            energyType === 'gas' ||
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
        setTariffResults([])

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
                        network_operator_id:
                            selectedNetworkOperator.network_operator_id,
                        energy_type: energyType,
                        ...(energyType === 'gas'
                            ? {
                                  consumption_kwh: consumptionValue,
                                  network_level: 3,
                                  tariff_type: 'nicht_leistungsgemessen',
                              }
                            : {
                                  consumption_kwh: consumptionValue,
                                  network_level: 7,
                                  tariff_type: 'nicht_gemessen',
                              }),
                        customer_type: customerType,
                        calculation_date: getLocalDate(),
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

            if (energyType === 'gas') {
                return
            }

            const tariffResponse = await fetch(
                'http://127.0.0.1:8000/calculator/tariffs',
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: `Bearer ${token}`,
                    },
                    body: JSON.stringify({
                        postal_code_id: selectedPostalCode.id,
                        network_operator_id:
                            selectedNetworkOperator.network_operator_id,
                        consumption_kwh: consumptionValue,
                        energy_type: energyType,
                        customer_type: customerType,
                        calculation_date: getLocalDate(),
                        network_level: 7,
                        tariff_type: 'nicht_gemessen',
                        meter_type: 'standard',
                    }),
                }
            )

            const tariffData = await tariffResponse.json()

            if (!tariffResponse.ok) {
                throw new Error(
                    tariffData.detail ||
                        'Die Tarife konnten nicht berechnet werden.'
                )
            }

            setTariffResults(tariffData)

            console.log('Tariff results:', tariffData)
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

            {calculationResult && energyType === 'gas' && (
                <div
                    className="tariff-calculator-card"
                    style={{ marginTop: '24px' }}
                >
                    <div className="tariff-calculator-header">
                        <div className="tariff-calculator-icon">€</div>

                        <div>
                            <h2>Gas-Netznutzung</h2>
                            <p>
                                {selectedPostalCode?.postal_code}{' '}
                                {selectedPostalCode?.city}
                                {' · '}
                                {selectedNetworkOperator?.network_operator_name ||
                                    selectedNetworkOperator?.name}
                            </p>
                        </div>
                    </div>

                    <div className="tariff-form">
                        <div className="tariff-form-grid">
                            <div className="form-field">
                                <label>Jahresverbrauch</label>
                                <strong>
                                    {Number(
                                        calculationResult.consumption_kwh
                                    ).toLocaleString('de-AT', {
                                        maximumFractionDigits: 2,
                                    })}{' '}
                                    kWh
                                </strong>
                            </div>

                            <div className="form-field">
                                <label>Berechneter Verbrauch</label>
                                <strong>
                                    {Number(
                                        calculationResult.consumption_kwh
                                    ).toLocaleString('de-AT', {
                                        maximumFractionDigits: 2,
                                    })}{' '}
                                    kWh
                                </strong>
                            </div>

                            <div className="form-field">
                                <label>Arbeitspreis</label>
                                <strong>
                                    {formatEuro(
                                        calculationResult.network.work_price
                                    )}
                                </strong>
                            </div>

                            <div className="form-field">
                                <label>Pauschale pro Jahr</label>
                                <strong>
                                    {formatEuro(
                                        calculationResult.network.base_price
                                    )}
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
                                Netznutzungsentgelt
                            </div>

                            <strong style={{ fontSize: '30px' }}>
                                {formatEuro(
                                    calculationResult.network
                                        .network_usage_subtotal
                                )}
                            </strong>
                        </div>

                        <p style={{ marginTop: '16px' }}>
                            Messentgelt, Abgaben und Umsatzsteuer sind
                            in diesem Zwischenstand noch nicht enthalten.
                        </p>
                    </div>
                </div>
            )}

            {tariffResults.length > 0 && energyType === 'strom' && (
                <section className="tariff-results-section">
                    <div className="tariff-results-heading">
                        <div>
                            <span className="tariff-results-eyebrow">
                                TARIFVERGLEICH
                            </span>

                            <h2>Passende Stromtarife</h2>

                            <p>
                                {tariffResults[0].postal_code}{' '}
                                {tariffResults[0].city}
                                {' · '}
                                {tariffResults[0].network_operator_name}
                                {' · '}
                                {Number(
                                    tariffResults[0].consumption_kwh
                                ).toLocaleString('de-AT')}{' '}
                                kWh / Jahr
                            </p>
                        </div>

                        <div className="tariff-results-count">
                            {tariffResults.length}{' '}
                            {tariffResults.length === 1
                                ? 'Tarif'
                                : 'Tarife'}
                        </div>
                    </div>

                    <div className="tariff-results-list">
                        {tariffResults.map((tariff, index) => (
                            <article
                                className="supplier-tariff-card"
                                key={tariff.tariff_id}
                            >
                                <div className="supplier-tariff-main">
                                    <div className="supplier-tariff-provider">
                                        <div className="supplier-logo-placeholder">
                                            {tariff.provider_name
                                                ?.charAt(0)
                                                .toUpperCase()}
                                        </div>

                                        <div>
                                            <div className="supplier-name-row">
                                                <span className="supplier-name">
                                                    {tariff.provider_name}
                                                </span>

                                                {index === 0 && (
                                                    <span className="tariff-best-price-badge">
                                                        Günstigster Tarif
                                                    </span>
                                                )}
                                            </div>

                                            <h3>{tariff.tariff_name}</h3>

                                            <div className="supplier-tariff-location">
                                                {tariff.postal_code}{' '}
                                                {tariff.city}
                                                <span>•</span>
                                                {tariff.network_operator_name}
                                            </div>
                                        </div>
                                    </div>

                                    <div className="supplier-tariff-price">
                                        <span>Gesamtkosten</span>

                                        <strong>
                                            {formatEuro(
                                                tariff.total_annual_cost
                                            )}
                                        </strong>

                                        <small>pro Jahr</small>
                                    </div>
                                </div>

                                {(() => {
                                    const energy =
                                        Number(tariff.energy_cost || 0) -
                                        Number(tariff.bonus || 0)
                                    const network = Number(
                                        tariff.network_tariff || 0
                                    )
                                    const taxes =
                                        Number(
                                            tariff.regulatory_charges || 0
                                        ) +
                                        Number(tariff.usage_fee || 0)
                                    const base = Number(
                                        tariff.base_price_year || 0
                                    )

                                    const total =
                                        energy + network + taxes + base

                                    const energyPct =
                                        total > 0
                                            ? (energy / total) * 100
                                            : 0
                                    const networkPct =
                                        total > 0
                                            ? (network / total) * 100
                                            : 0
                                    const taxesPct =
                                        total > 0
                                            ? (taxes / total) * 100
                                            : 0
                                    const basePct =
                                        total > 0
                                            ? (base / total) * 100
                                            : 0

                                    const energyEnd = energyPct
                                    const networkEnd =
                                        energyEnd + networkPct
                                    const taxesEnd =
                                        networkEnd + taxesPct

                                    return (
                                        <div className="supplier-tariff-visual">
                                            <div className="tariff-donut-area">
                                                <div
                                                    className="tariff-donut"
                                                    style={{
                                                        background: `conic-gradient(
                                                            #087443 0% ${energyEnd}%,
                                                            #1769d2 ${energyEnd}% ${networkEnd}%,
                                                            #f3b52b ${networkEnd}% ${taxesEnd}%,
                                                            #9aa6ad ${taxesEnd}% 100%
                                                        )`,
                                                    }}
                                                >
                                                    <div className="tariff-donut-center">
                                                        <strong>
                                                            {formatEuro(
                                                                tariff.total_annual_cost
                                                            )}
                                                        </strong>
                                                        <span>pro Jahr</span>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="tariff-donut-legend">
                                                <div>
                                                    <span className="tariff-legend-dot tariff-legend-energy" />
                                                    <div>
                                                        <span>
                                                            Energiekosten
                                                        </span>
                                                        <strong>
                                                            {formatEuro(
                                                                energy
                                                            )}{' '}
                                                            ({Math.round(
                                                                energyPct
                                                            )}%)
                                                        </strong>
                                                    </div>
                                                </div>

                                                <div>
                                                    <span className="tariff-legend-dot tariff-legend-network" />
                                                    <div>
                                                        <span>
                                                            Netzentgelte
                                                        </span>
                                                        <strong>
                                                            {formatEuro(
                                                                network
                                                            )}{' '}
                                                            ({Math.round(
                                                                networkPct
                                                            )}%)
                                                        </strong>
                                                    </div>
                                                </div>

                                                <div>
                                                    <span className="tariff-legend-dot tariff-legend-taxes" />
                                                    <div>
                                                        <span>
                                                            Abgaben &amp;
                                                            Steuern
                                                        </span>
                                                        <strong>
                                                            {formatEuro(
                                                                taxes
                                                            )}{' '}
                                                            ({Math.round(
                                                                taxesPct
                                                            )}%)
                                                        </strong>
                                                    </div>
                                                </div>

                                                <div>
                                                    <span className="tariff-legend-dot tariff-legend-base" />
                                                    <div>
                                                        <span>
                                                            Grundgebühr
                                                        </span>
                                                        <strong>
                                                            {formatEuro(
                                                                base
                                                            )}{' '}
                                                            ({Math.round(
                                                                basePct
                                                            )}%)
                                                        </strong>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="tariff-reference-offer">
                                                <div className="tariff-reference-price">
                                                    <span>🍃</span>

                                                    <strong>
                                                        {Number(
                                                            tariff.work_price_cent_kwh
                                                        ).toLocaleString(
                                                            'de-AT',
                                                            {
                                                                minimumFractionDigits: 2,
                                                                maximumFractionDigits: 3,
                                                            }
                                                        )}{' '}
                                                        ct/kWh
                                                    </strong>
                                                </div>

                                                <div className="tariff-reference-feature">
                                                    <span>✓</span>
                                                    Tarif geprüft
                                                </div>

                                                <div className="tariff-reference-feature">
                                                    <span>✓</span>
                                                    Für diesen Netzbetreiber
                                                    verfügbar
                                                </div>

                                                {Number(tariff.bonus) >
                                                    0 && (
                                                    <div className="tariff-reference-feature">
                                                        <span>✓</span>
                                                        Bonus{' '}
                                                        {formatEuro(
                                                            tariff.bonus
                                                        )}
                                                    </div>
                                                )}

                                                <button
                                                    type="button"
                                                    className="tariff-offer-button tariff-reference-offer-button"
                                                >
                                                    Zum Angebot
                                                    <span>→</span>
                                                </button>
                                            </div>
                                        </div>
                                    )
                                })()}

                                <div className="supplier-tariff-footer">
                                    <div className="supplier-tariff-features">
                                        <span>✓ Tarif geprüft</span>
                                        <span>✓ Für diesen Netzbetreiber verfügbar</span>
                                    </div>

                                    <div className="supplier-tariff-actions">
                                        <button
                                            type="button"
                                            className="tariff-details-button"
                                            onClick={() => {
                                                setSelectedTariffResult(tariff)
                                                setCommissionVisible(false)
                                                setCommissionData(null)
                                                setCommissionError('')
                                                setNetworkDetailsOpen(false)
                                            }}
                                        >
                                            Alle Details anzeigen
                                            <span>→</span>
                                        </button>

                                        <button
                                            type="button"
                                            className="tariff-offer-button"
                                        >
                                            Zum Angebot
                                            <span>→</span>
                                        </button>
                                    </div>
                                </div>
                            </article>
                        ))}
                    </div>
                </section>
            )}

            {selectedTariffResult &&
                calculationResult &&
                energyType === 'strom' && (
                    <>
                        <div
                            className="tariff-detail-backdrop"
                            onClick={() => setSelectedTariffResult(null)}
                        />

                        <aside className="tariff-detail-drawer">
                            <div className="tariff-detail-topbar">
                                <button
                                    type="button"
                                    className="tariff-detail-back"
                                    onClick={() =>
                                        setSelectedTariffResult(null)
                                    }
                                >
                                    ← Zurück zur Tarifübersicht
                                </button>

                                <button
                                    type="button"
                                    className="tariff-detail-close"
                                    onClick={() =>
                                        setSelectedTariffResult(null)
                                    }
                                    aria-label="Tarifdetails schließen"
                                >
                                    ×
                                </button>
                            </div>

                            <div className="tariff-detail-header">
                                <div>
                                    <div className="tariff-detail-provider-name">
                                        {selectedTariffResult.provider_name}
                                    </div>

                                    <div className="tariff-detail-title-row">
                                        <h2>
                                            {selectedTariffResult.tariff_name}
                                        </h2>

                                        <span className="tariff-detail-tip">
                                            🍃 Unser Tipp
                                        </span>
                                    </div>

                                    <div className="tariff-detail-location">
                                        {selectedTariffResult.postal_code}{' '}
                                        {selectedTariffResult.city}
                                        {' · '}
                                        {
                                            selectedTariffResult
                                                .network_operator_name
                                        }
                                    </div>
                                </div>

                                <div className="tariff-detail-price">
                                    <strong>
                                        {Number(
                                            selectedTariffResult
                                                .work_price_cent_kwh
                                        ).toLocaleString('de-AT', {
                                            minimumFractionDigits: 2,
                                            maximumFractionDigits: 3,
                                        })}{' '}
                                        ct/kWh
                                    </strong>

                                    <span>
                                        {formatEuro(
                                            selectedTariffResult
                                                .total_annual_cost
                                        )}{' '}
                                        pro Jahr
                                    </span>

                                    <small>
                                        bei{' '}
                                        {Number(
                                            selectedTariffResult
                                                .consumption_kwh
                                        ).toLocaleString('de-AT')}{' '}
                                        kWh
                                    </small>
                                </div>
                            </div>

                            <div className="tariff-detail-tabs">
                                <button type="button" className="active">
                                    Übersicht
                                </button>
                                <button type="button">
                                    Vertragsinfos
                                </button>
                            </div>

                            <div className="tariff-detail-scroll">
                                {(() => {
                                    const energy =
                                        Number(selectedTariffResult.energy_cost || 0) -
                                        Number(selectedTariffResult.bonus || 0)

                                    const network =
                                        Number(selectedTariffResult.network_tariff || 0)

                                    const taxes =
                                        Number(
                                            selectedTariffResult.regulatory_charges || 0
                                        ) +
                                        Number(selectedTariffResult.usage_fee || 0)

                                    const base =
                                        Number(
                                            selectedTariffResult.base_price_year || 0
                                        )

                                    const total =
                                        energy + network + taxes + base

                                    const energyPct =
                                        total > 0 ? (energy / total) * 100 : 0
                                    const networkPct =
                                        total > 0 ? (network / total) * 100 : 0
                                    const taxesPct =
                                        total > 0 ? (taxes / total) * 100 : 0

                                    const energyEnd = energyPct
                                    const networkEnd =
                                        energyEnd + networkPct
                                    const taxesEnd =
                                        networkEnd + taxesPct

                                    return (
                                        <section className="tariff-overview-card">
                                            <div
                                                className="tariff-overview-donut"
                                                style={{
                                                    background: `conic-gradient(
                                                        #087443 0% ${energyEnd}%,
                                                        #1769d2 ${energyEnd}% ${networkEnd}%,
                                                        #f3b52b ${networkEnd}% ${taxesEnd}%,
                                                        #9aa6ad ${taxesEnd}% 100%
                                                    )`,
                                                }}
                                            >
                                                <div className="tariff-overview-donut-hole">
                                                    <strong>
                                                        {formatEuro(
                                                            selectedTariffResult
                                                                .total_annual_cost
                                                        )}
                                                    </strong>
                                                    <span>pro Jahr</span>
                                                </div>
                                            </div>

                                            <div className="tariff-overview-legend">
                                                <div>
                                                    <span className="tariff-overview-dot energy" />
                                                    <span>Energiekosten</span>
                                                    <strong>
                                                        {formatEuro(energy)}
                                                    </strong>
                                                    <small>
                                                        ({Math.round(energyPct)}%)
                                                    </small>
                                                </div>

                                                <button
                                                    type="button"
                                                    className="tariff-overview-network-row"
                                                    onClick={() =>
                                                        setNetworkDetailsOpen(
                                                            (value) => !value
                                                        )
                                                    }
                                                >
                                                    <span className="tariff-overview-dot network" />
                                                    <span>Netzentgelte</span>
                                                    <strong>
                                                        {formatEuro(network)}
                                                    </strong>
                                                    <small>
                                                        ({Math.round(networkPct)}%)
                                                        {' '}
                                                        {networkDetailsOpen
                                                            ? '▲'
                                                            : '▼'}
                                                    </small>
                                                </button>

                                                <div>
                                                    <span className="tariff-overview-dot taxes" />
                                                    <span>
                                                        Abgaben &amp; Steuern
                                                    </span>
                                                    <strong>
                                                        {formatEuro(taxes)}
                                                    </strong>
                                                    <small>
                                                        ({Math.round(taxesPct)}%)
                                                    </small>
                                                </div>

                                                <div>
                                                    <span className="tariff-overview-dot base" />
                                                    <span>Grundgebühr</span>
                                                    <strong>
                                                        {formatEuro(base)}
                                                    </strong>
                                                    <small>
                                                        (
                                                        {Math.round(
                                                            total > 0
                                                                ? (base / total) * 100
                                                                : 0
                                                        )}
                                                        %)
                                                    </small>
                                                </div>
                                            </div>
                                        </section>
                                    )
                                })()}

                                {networkDetailsOpen && (
                                    <section className="tariff-network-details">
                                        <div className="tariff-network-details-head">
                                            <div>
                                                <strong>
                                                    Netzentgelte im Detail
                                                </strong>
                                                <span>
                                                    {
                                                        selectedTariffResult
                                                            .network_operator_name
                                                    }
                                                </span>
                                            </div>

                                            <button
                                                type="button"
                                                onClick={() =>
                                                    setNetworkDetailsOpen(false)
                                                }
                                                aria-label="Netzentgelte schließen"
                                            >
                                                ×
                                            </button>
                                        </div>

                                        <div className="tariff-network-detail-row main">
                                            <span>Netznutzungsentgelt</span>
                                            <strong>
                                                {formatEuro(
                                                    calculationResult.network
                                                        .base_price +
                                                        calculationResult.network
                                                            .work_price
                                                )}
                                            </strong>
                                        </div>

                                        <div className="tariff-network-detail-row sub">
                                            <span>Grundpreis Netz</span>
                                            <span>
                                                {formatEuro(
                                                    calculationResult.network
                                                        .base_price
                                                )}
                                            </span>
                                        </div>

                                        <div className="tariff-network-detail-row sub">
                                            <span>Arbeitspreis Netz</span>
                                            <span>
                                                {formatEuro(
                                                    calculationResult.network
                                                        .work_price
                                                )}
                                            </span>
                                        </div>

                                        <div className="tariff-network-detail-row">
                                            <span>Netzverlustentgelt</span>
                                            <strong>
                                                {formatEuro(
                                                    calculationResult.network
                                                        .network_loss
                                                )}
                                            </strong>
                                        </div>

                                        <div className="tariff-network-detail-row">
                                            <span>
                                                {calculationResult.network
                                                    .metering_cost_source ===
                                                'fallback_max'
                                                    ? 'Messentgelt (Höchstpreis)'
                                                    : 'Messentgelt'}
                                            </span>
                                            <strong>
                                                {formatEuro(
                                                    calculationResult.network
                                                        .metering_cost
                                                )}
                                            </strong>
                                        </div>

                                        <div className="tariff-network-detail-row total">
                                            <span>Netztarif</span>
                                            <strong>
                                                {formatEuro(
                                                    calculationResult.network
                                                        .total_network_tariff
                                                )}
                                            </strong>
                                        </div>
                                    </section>
                                )}

                                <div className="tariff-reference-middle">
                                    <section className="tariff-reference-highlights">
                                        <h3>🌿 Tarif-Highlights</h3>

                                        <div>
                                            <span>✓</span>
                                            Tarif für den gewählten
                                            Netzbetreiber verfügbar
                                        </div>

                                        <div>
                                            <span>✓</span>
                                            Netz- und Abgabenkosten berücksichtigt
                                        </div>

                                        <div>
                                            <span>✓</span>
                                            Tarifkosten transparent aufgeschlüsselt
                                        </div>
                                    </section>

                                    <section className="tariff-provision-card">
                                        <div className="tariff-provision-reference-title">
                                            <span>◉</span>
                                            <strong>
                                                Provisionen anzeigen
                                            </strong>
                                        </div>

                                        <p>
                                            Schieben Sie den Regler nach rechts,
                                            um die Provision anzuzeigen.
                                        </p>

                                        <div className="tariff-provision-reference-control">
                                            <span
                                                className={
                                                    commissionVisible
                                                        ? 'unlocked'
                                                        : ''
                                                }
                                            >
                                                <svg
                                                    viewBox="0 0 24 24"
                                                    fill="none"
                                                    xmlns="http://www.w3.org/2000/svg"
                                                    aria-hidden="true"
                                                >
                                                    <rect
                                                        x="6"
                                                        y="10"
                                                        width="12"
                                                        height="10"
                                                        rx="2"
                                                        fill="currentColor"
                                                    />
                                                    <path
                                                        d={
                                                            commissionVisible
                                                                ? "M9 10V7.5C9 5.6 10.4 4 12.3 4C13.4 4 14.4 4.5 15 5.3"
                                                                : "M8.5 10V7.5C8.5 5.6 10.1 4 12 4C13.9 4 15.5 5.6 15.5 7.5V10"
                                                        }
                                                        stroke="currentColor"
                                                        strokeWidth="2"
                                                        strokeLinecap="round"
                                                    />
                                                    <circle
                                                        cx="12"
                                                        cy="15"
                                                        r="1.3"
                                                        fill="white"
                                                    />
                                                    <path
                                                        d="M12 16.2V18"
                                                        stroke="white"
                                                        strokeWidth="1.3"
                                                        strokeLinecap="round"
                                                    />
                                                </svg>
                                            </span>

                                            <button
                                                type="button"
                                                className={`tariff-provision-slider ${
                                                    commissionVisible
                                                        ? 'active'
                                                        : ''
                                                }`}
                                                onClick={toggleTariffCommission}
                                                aria-pressed={
                                                    commissionVisible
                                                }
                                            >
                                                <i />
                                            </button>

                                            <span
                                                className="tariff-provision-eye"
                                                aria-hidden="true"
                                            >
                                                <svg
                                                    viewBox="0 0 24 24"
                                                    fill="none"
                                                    xmlns="http://www.w3.org/2000/svg"
                                                >
                                                    <path
                                                        d="M2.5 12C4.7 8.2 8 6.2 12 6.2C16 6.2 19.3 8.2 21.5 12C19.3 15.8 16 17.8 12 17.8C8 17.8 4.7 15.8 2.5 12Z"
                                                        stroke="currentColor"
                                                        strokeWidth="2"
                                                        strokeLinecap="round"
                                                        strokeLinejoin="round"
                                                    />
                                                    <circle
                                                        cx="12"
                                                        cy="12"
                                                        r="3.2"
                                                        fill="currentColor"
                                                    />
                                                </svg>
                                            </span>
                                        </div>

                                        {commissionVisible && (
                                            <div className="tariff-provision-result">
                                                {commissionLoading && (
                                                    <span>
                                                        Provision wird geladen …
                                                    </span>
                                                )}

                                                {!commissionLoading &&
                                                    commissionError && (
                                                        <span className="error">
                                                            {commissionError}
                                                        </span>
                                                    )}

                                                {!commissionLoading &&
                                                    !commissionError &&
                                                    commissionData && (
                                                        <>
                                                            <span>
                                                                Ihre Provision
                                                            </span>
                                                            <strong>
                                                                {formatEuro(
                                                                    commissionData
                                                                        .agent_commission
                                                                )}
                                                            </strong>
                                                        </>
                                                    )}
                                            </div>
                                        )}
                                    </section>
                                </div>

                                <section className="tariff-reference-info">
                                    <div className="tariff-reference-info-icon">
                                        <svg
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            xmlns="http://www.w3.org/2000/svg"
                                            aria-hidden="true"
                                        >
                                            <path
                                                d="M9 18h6M10 21h4M8.4 14.5C6.9 13.4 6 11.7 6 9.8A6 6 0 0 1 18 9.8c0 1.9-.9 3.6-2.4 4.7-.9.7-1.3 1.4-1.4 2.5H9.8c-.1-1.1-.5-1.8-1.4-2.5Z"
                                                stroke="currentColor"
                                                strokeWidth="1.8"
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                            />
                                            <path
                                                d="M12 2V1M4.9 4.2 4.2 3.5M19.1 4.2l.7-.7M3 10H2M22 10h-1"
                                                stroke="currentColor"
                                                strokeWidth="1.8"
                                                strokeLinecap="round"
                                            />
                                        </svg>
                                    </div>

                                    <div>
                                        <strong>
                                            {customerType === 'privat'
                                                ? 'Preisübersicht für Privatkunden'
                                                : 'Preisübersicht für Gewerbekunden'}
                                        </strong>
                                        <span>
                                            Der angezeigte Jahresbetrag (
                                            {formatEuro(
                                                selectedTariffResult
                                                    .total_annual_cost
                                            )}
                                            ) ergibt sich aus allen
                                            Kostenbestandteilen des Tarifs.
                                        </span>
                                    </div>
                                </section>
                            </div>

                            {tariffDocumentsOpen && (
                                <div className="tariff-documents-popover">
                                    <div className="tariff-documents-popover-header">
                                        <div>
                                            <strong>PDF Dokumente</strong>
                                            <span>
                                                Preisblatt, AGB, Vollmacht & Formular
                                            </span>
                                        </div>

                                        <button
                                            type="button"
                                            onClick={() =>
                                                setTariffDocumentsOpen(false)
                                            }
                                            aria-label="Dokumente schließen"
                                        >
                                            ×
                                        </button>
                                    </div>

                                    {tariffDocumentsLoading ? (
                                        <div className="tariff-documents-status">
                                            Dokumente werden geladen...
                                        </div>
                                    ) : tariffDocumentsError ? (
                                        <div className="tariff-documents-status tariff-documents-status-error">
                                            {tariffDocumentsError}
                                        </div>
                                    ) : tariffDocuments.length === 0 ? (
                                        <div className="tariff-documents-status">
                                            Für diesen Tarif sind noch keine PDF-Dokumente hinterlegt.
                                        </div>
                                    ) : (
                                        <div className="tariff-documents-popover-list">
                                            {tariffDocuments.map((documentItem) => {
                                                const labels = {
                                                    price_sheet: 'Preisblatt',
                                                    agb: 'AGB',
                                                    power_of_attorney: 'Vollmacht',
                                                    form: 'Formular',
                                                    other: 'Sonstiges',
                                                }

                                                return (
                                                    <button
                                                        type="button"
                                                        key={documentItem.id}
                                                        onClick={async () => {
                                                            try {
                                                                const token =
                                                                    localStorage.getItem(
                                                                        'access_token'
                                                                    )

                                                                const response =
                                                                    await fetch(
                                                                        `http://127.0.0.1:8000${documentItem.download_url}`,
                                                                        {
                                                                            headers: {
                                                                                Authorization:
                                                                                    `Bearer ${token}`,
                                                                            },
                                                                        }
                                                                    )

                                                                if (!response.ok) {
                                                                    throw new Error(
                                                                        'PDF konnte nicht geöffnet werden.'
                                                                    )
                                                                }

                                                                const blob =
                                                                    await response.blob()
                                                                const url =
                                                                    URL.createObjectURL(
                                                                        blob
                                                                    )

                                                                window.open(
                                                                    url,
                                                                    '_blank',
                                                                    'noopener,noreferrer'
                                                                )

                                                                window.setTimeout(
                                                                    () =>
                                                                        URL.revokeObjectURL(
                                                                            url
                                                                        ),
                                                                    60000
                                                                )
                                                            } catch (error) {
                                                                setTariffDocumentsError(
                                                                    error.message ||
                                                                        'PDF konnte nicht geöffnet werden.'
                                                                )
                                                            }
                                                        }}
                                                    >
                                                        <span className="tariff-document-pdf-icon">
                                                            PDF
                                                        </span>

                                                        <span className="tariff-document-name">
                                                            <strong>
                                                                {labels[
                                                                    documentItem
                                                                        .document_type
                                                                ] ||
                                                                    documentItem.document_type}
                                                            </strong>
                                                            <small>
                                                                {
                                                                    documentItem.file_name
                                                                }
                                                            </small>
                                                        </span>

                                                        <span className="tariff-document-open">
                                                            Öffnen →
                                                        </span>
                                                    </button>
                                                )
                                            })}
                                        </div>
                                    )}
                                </div>
                            )}

                            <div className="tariff-detail-footer">
                                <button
                                    type="button"
                                    className="tariff-pdf-button"
                                    onClick={async () => {
                                        if (tariffDocumentsOpen) {
                                            setTariffDocumentsOpen(false)
                                            return
                                        }

                                        setTariffDocumentsOpen(true)
                                        setTariffDocumentsLoading(true)
                                        setTariffDocumentsError('')

                                        try {
                                            const token =
                                                localStorage.getItem(
                                                    'access_token'
                                                )

                                            const response = await fetch(
                                                `http://127.0.0.1:8000/tariff-documents/tariffs/${selectedTariffResult.tariff_id}`,
                                                {
                                                    headers: {
                                                        Authorization:
                                                            `Bearer ${token}`,
                                                    },
                                                }
                                            )

                                            const data =
                                                await response.json()

                                            if (!response.ok) {
                                                throw new Error(
                                                    data.detail ||
                                                        'Dokumente konnten nicht geladen werden.'
                                                )
                                            }

                                            setTariffDocuments(data)
                                        } catch (error) {
                                            setTariffDocuments([])
                                            setTariffDocumentsError(
                                                error.message ||
                                                    'Dokumente konnten nicht geladen werden.'
                                            )
                                        } finally {
                                            setTariffDocumentsLoading(false)
                                        }
                                    }}
                                >
                                    <span className="tariff-pdf-icon">PDF</span>

                                    <span>
                                        <strong>PDF Formular herunterladen</strong>
                                    </span>
                                </button>

                                <button
                                    type="button"
                                    className="tariff-offer-button"
                                >
                                    Zum Angebot
                                    <span>→</span>
                                </button>
                            </div>
                        </aside>
                    </>
                )}

        </div>
    )
}

export default NewContract