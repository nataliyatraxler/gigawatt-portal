import vorversorgerList from '../data/gigawatt_vorversorger.json'
import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

const today = new Date().toISOString().slice(0, 10)

function OfferContract() {
    const { state: offer } = useLocation()
    const navigate = useNavigate()
    const [sameAccountHolder, setSameAccountHolder] = useState(true)
    const [digitalSignature, setDigitalSignature] = useState(true)
    const [supplierSearch, setSupplierSearch] = useState('')
    const [selectedSupplier, setSelectedSupplier] = useState('')
    const [supplierOpen, setSupplierOpen] = useState(false)

    const [zpn, setZpn] = useState(offer?.zpn || '')
    const [iban, setIban] = useState('')
    const [bic, setBic] = useState('')
    const [bankName, setBankName] = useState('')
    const [ibanLoading, setIbanLoading] = useState(false)
    const [ibanError, setIbanError] = useState('')
    const [validationAttempted, setValidationAttempted] = useState(false)

    const validateOfferForm = (event) => {
        event.preventDefault()
        setValidationAttempted(true)

        const form = event.currentTarget
        const fields = Array.from(
            form.querySelectorAll('input, select')
        )

        const uid = form.querySelector('[name="uidNumber"]')
        const fn = form.querySelector('[name="companyRegisterNumber"]')

        const companyIdMissing =
            offer?.customerType === 'gewerbe' &&
            !uid?.value.trim() &&
            !fn?.value.trim()

        for (const field of fields) {
            if (field === uid || field === fn) {
                field.setCustomValidity(
                    companyIdMissing
                        ? 'Bitte UID-Nummer oder Firmenbuchnummer eingeben.'
                        : ''
                )
            }
        }

        const firstInvalid = fields.find(
            (field) => !field.checkValidity()
        )

        if (firstInvalid) {
            firstInvalid.focus()
            firstInvalid.scrollIntoView({
                behavior: 'smooth',
                block: 'center',
            })
        }
    }


    const lookupBankData = async (rawIban) => {
        const cleanIban = rawIban.replace(/\s/g, '').toUpperCase()

        if (cleanIban.length < 15) {
            return
        }

        setIbanLoading(true)
        setIbanError('')

        try {
            const response = await fetch(
                `https://openiban.com/validate/${encodeURIComponent(cleanIban)}?getBIC=true&validateBankCode=true`
            )

            if (!response.ok) {
                throw new Error('Bank lookup failed')
            }

            const data = await response.json()

            if (!data.valid || !data.bankData) {
                setIbanError('IBAN konnte nicht bestätigt werden.')
                return
            }

            setBic(data.bankData.bic || '')
            setBankName(data.bankData.name || '')

            if (!data.bankData.bic || !data.bankData.name) {
                setIbanError('Bankdaten wurden nicht vollständig gefunden.')
            }
        } catch (error) {
            setIbanError('Bankdaten konnten nicht automatisch geladen werden.')
        } finally {
            setIbanLoading(false)
        }
    }


    if (!offer) {
        return (
            <section className="offer-empty">
                <h1>Kein Angebot ausgewählt</h1>
                <p>Wähle zuerst einen Tarif aus der Tarifübersicht aus.</p>
                <button
                    type="button"
                    className="offer-primary-button"
                    onClick={() =>
                        navigate('/contracts/new', {
                            state: { restoreOffer: offer },
                        })
                    }
                >
                    Zur Tarifübersicht
                </button>
            </section>
        )
    }

    const tariffName =
        offer.tariff?.tariff_name ||
        offer.tariff?.name ||
        offer.tariff?.provider_name ||
        'Ausgewählter Tarif'

    const providerName =
        offer.tariff?.provider_name ||
        offer.tariff?.provider?.name ||
        'Energielieferant'

    const total =
        offer.tariff?.gross_total ||
        offer.tariff?.annual_cost ||
        offer.calculationResult?.gross_total

    const formatEuro = (value) =>
        Number(value || 0).toLocaleString('de-AT', {
            style: 'currency',
            currency: 'EUR',
        })

    return (
        <div className="offer-shell">
            <header className="offer-shell-header">
                <span>
                    <strong>GIGAWATT</strong>{' '}
                    <span>Solution</span>
                </span>

                <span className="offer-shell-icons">▦ &nbsp; ◉</span>
            </header>

            <section className="offer-page">
            <div className="offer-page-head">
                <div>
                    <button
                        type="button"
                        className="offer-back-button"
                        onClick={() =>
                        navigate('/contracts/new', {
                            state: { restoreOffer: offer },
                        })
                    }
                    >
                        ← Zurück zur Tarifübersicht
                    </button>
                    <p className="offer-eyebrow">NEUER VERTRAG</p>
                    <h1>Neuen Auftrag erfassen</h1>
                    <p>Alle Auftragsdaten auf einen Blick</p>
                </div>

                <span className="offer-status">Entwurf</span>
            </div>

            <div className="offer-selected-tariff">
                <div>
                    <span>Ausgewähltes Angebot</span>
                    <strong>{providerName} · {tariffName}</strong>
                    <small>
                        {offer.energyType === 'gas' ? 'Gas' : 'Strom'} ·{' '}
                        {Number(offer.consumption || 0).toLocaleString('de-AT')} kWh/Jahr
                    </small>
                </div>

                {total && <b>{formatEuro(total)} / Jahr</b>}
            </div>

            <form
                className={`offer-form ${validationAttempted ? 'offer-validation-attempted' : ''}`}
                noValidate
                onSubmit={validateOfferForm}
                onInput={(event) => {
                    if (event.target.validity?.customError) {
                        const form = event.currentTarget
                        const uid = form.querySelector('[name="uidNumber"]')
                        const fn = form.querySelector('[name="companyRegisterNumber"]')

                        if (uid?.value.trim() || fn?.value.trim()) {
                            uid?.setCustomValidity('')
                            fn?.setCustomValidity('')
                        }
                    }

                    if (validationAttempted) {
                        event.currentTarget.querySelectorAll('input, select').forEach(
                            (field) => {
                                field.setAttribute(
                                    'aria-invalid',
                                    String(!field.checkValidity())
                                )
                            }
                        )
                    }
                }}
            >
                <div className="offer-column">
                    <section className="offer-card">
                        <h2>♙ Kundendaten</h2>

                        <label>
                            Stammkundensuche
                            <input placeholder="Stammkundensuche / Referenznummer" />
                        </label>



                        {offer.customerType === 'gewerbe' && (
                            <>
                                <label>
                                    Firmenname *
                                    <input
                                        required
                                        placeholder="Firmenname"
                                    />
                                </label>

                                <div className="offer-grid">
                                    <label>
                                        UID-Nummer (ATU)
                                        <input
                                            name="uidNumber"
                                            placeholder="ATU / UID-Nummer"
                                            maxLength={11}
                                        />
                                    </label>

                                    <label>
                                        Firmenbuchnummer (FN)
                                        <input
                                            name="companyRegisterNumber"
                                            placeholder="Firmenbuchnummer (FN)"
                                        />
                                    </label>
                                </div>
                            </>
                        )}

                        <div className="offer-grid">
                            <label>
                                Anrede
                                <select defaultValue="">
                                    <option value="" disabled>Bitte wählen</option>
                                    <option>Frau</option>
                                    <option>Herr</option>
                                    <option>Divers</option>
                                </select>
                            </label>

                            <label>
                                Titel
                                <select defaultValue="Kein Titel">
                                    <option>Kein Titel</option>
                                    <option>Dr.</option>
                                    <option>Mag.</option>
                                </select>
                            </label>

                            <label>
                                Vorname *
                                <input required placeholder="Vorname" />
                            </label>

                            <label>
                                Nachname *
                                <input required placeholder="Nachname" />
                            </label>
                        </div>

                        <label>
                            Geburtsdatum *
                            <input required type="date" />
                        </label>

                        <hr />
                        <h3>Lieferadresse</h3>

                        <label>
                            Land
                            <select defaultValue="Österreich">
                                <option>Österreich</option>
                            </select>
                        </label>

                        <div className="offer-grid">
                            <label>
                                Postleitzahl *
                                <input required defaultValue={offer.postalCode} placeholder="PLZ" />
                            </label>

                            <label>
                                Ort *
                                <input required defaultValue={offer.city} placeholder="Ort" />
                            </label>

                            <label>
                                Straße *
                                <input required defaultValue={offer.street} placeholder="Straße" />
                            </label>

                            <label>
                                Hausnummer *
                                <input required defaultValue={offer.houseNumber} placeholder="Nr." />
                            </label>

                            <label>
                                Stiege
                                <input placeholder="Stiege" />
                            </label>

                            <label>
                                Türnummer
                                <input placeholder="Tür" />
                            </label>
                        </div>

                        <hr />
                        <h3>Kontaktdaten</h3>

                        <label>
                            Festnetznummer
                            <input type="tel" placeholder="Festnetz" />
                        </label>

                        <label>
                            Mobilnummer *
                            <input
                                required
                                type="tel"
                                placeholder="Mobilnummer"
                            />
                        </label>

                        <label>
                            E-Mail-Adresse *
                            <input required type="email" placeholder="name@beispiel.at" />
                        </label>
                    </section>

                    <section className="offer-card">
                        <h2>▣ Bankverbindung</h2>

                        <label className="offer-check">
                            <input
                                type="checkbox"
                                checked={sameAccountHolder}
                                onChange={(event) => setSameAccountHolder(event.target.checked)}
                            />
                            Kontoinhaber entspricht Vertragsnehmer
                        </label>

                        <label>
                            Name des Kontoinhabers *
                            <input
                                required
                                disabled={sameAccountHolder}
                                placeholder={sameAccountHolder ? 'Wird aus den Kundendaten übernommen' : 'Name des Kontoinhabers'}
                            />
                        </label>

                        <label>
                                IBAN *
                                <input
                                    required
                                    placeholder="AT00 0000 0000 0000 0000"
                                    value={iban}
                                    onChange={(event) => {
                                        setIban(event.target.value)
                                        setIbanError('')
                                    }}
                                    onBlur={() => lookupBankData(iban)}
                                />
                            </label>

                        <div className="offer-grid">
                                <label>
                                    BIC
                                    <input
                                        placeholder="BIC"
                                        value={bic}
                                        onChange={(event) => setBic(event.target.value.toUpperCase())}
                                    />
                                </label>
                                <label>
                                    Name der Bank
                                    <input
                                        placeholder="Bankname"
                                        value={bankName}
                                        onChange={(event) => setBankName(event.target.value)}
                                    />
                                </label>
                            </div>

                            {ibanLoading && (
                                <p className="offer-hint">Bankdaten werden gesucht …</p>
                            )}

                            {ibanError && (
                                <p className="offer-hint">{ibanError}</p>
                            )}
                    </section>
                </div>

                <div className="offer-column">
                    <section className="offer-card">
                        <h2>ϟ Lieferstelle</h2>

                        <h3>Zählerdaten</h3>

                        <label>
                            Zählpunktbezeichnung *
                            <input
                                required
                                value={zpn}
                                onChange={(event) => {
                                    const value = event.target.value
                                        .toUpperCase()
                                        .slice(0, 33)
                                    setZpn(value)
                                }}
                                placeholder="AT..."
                                minLength={33}
                                maxLength={33}
                                pattern="AT.{31}"
                                title="Die Zählpunktbezeichnung muss genau 33 Zeichen lang sein und mit AT beginnen."
                            />

                            <div
                                style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    gap: '12px',
                                    marginTop: '7px',
                                    fontSize: '13px',
                                    fontWeight: 600,
                                }}
                            >
                                <span
                                    style={{
                                        color:
                                            zpn.length === 33 &&
                                            zpn.startsWith('AT')
                                                ? '#17834f'
                                                : '#c62828',
                                    }}
                                >
                                    {zpn.length === 33 &&
                                    zpn.startsWith('AT')
                                        ? '✓ Zählpunktbezeichnung vollständig'
                                        : zpn.length < 33
                                          ? `Es fehlen noch ${33 - zpn.length} Zeichen.`
                                          : 'Die Zählpunktbezeichnung muss mit AT beginnen.'}
                                </span>

                                <span
                                    style={{
                                        color:
                                            zpn.length === 33 &&
                                            zpn.startsWith('AT')
                                                ? '#17834f'
                                                : '#c62828',
                                        whiteSpace: 'nowrap',
                                    }}
                                >
                                    {zpn.length} / 33 Zeichen
                                </span>
                            </div>
                        </label>

                        <label>
                            Zählernummer
                            <input placeholder="Zählernummer" />
                        </label>

                        <hr />
                        <h3>Liefertermin & Vorversorger</h3>

                        <div className="offer-fieldset">
                            <label className="offer-radio">
                                <input type="radio" name="supplyType" defaultChecked />
                                Lieferantenwechsel
                            </label>
                            <label className="offer-radio">
                                <input type="radio" name="supplyType" />
                                Neuanmeldung
                            </label>
                        </div>

                        <div className="offer-supplier-field">
                            <label htmlFor="offer-supplier-search">
                                Bisheriger Energielieferant *
                            </label>

                            <input
                                id="offer-supplier-search"
                                type="text"
                                required
                                autoComplete="off"
                                placeholder="Vorversorger suchen..."
                                value={supplierSearch}
                                role="combobox"
                                aria-expanded={supplierOpen}
                                aria-controls="offer-supplier-options"
                                aria-autocomplete="list"
                                onFocus={() => setSupplierOpen(true)}
                                onChange={(event) => {
                                    setSupplierSearch(event.target.value)
                                    setSelectedSupplier('')
                                    setSupplierOpen(true)
                                }}
                                onBlur={() => {
                                    window.setTimeout(() => setSupplierOpen(false), 150)
                                }}
                                onKeyDown={(event) => {
                                    if (event.key === 'Escape') {
                                        setSupplierOpen(false)
                                    }
                                }}
                            />

                            {supplierOpen && (
                                <div
                                    id="offer-supplier-options"
                                    className="offer-supplier-options"
                                    role="listbox"
                                >
                                    {vorversorgerList
                                        .filter((supplier) =>
                                            supplier.toLocaleLowerCase('de-AT')
                                                .includes(
                                                    supplierSearch
                                                        .trim()
                                                        .toLocaleLowerCase('de-AT')
                                                )
                                        )
                                        .slice(0, 30)
                                        .map((supplier) => (
                                            <button
                                                key={supplier}
                                                type="button"
                                                role="option"
                                                aria-selected={selectedSupplier === supplier}
                                                onMouseDown={(event) => event.preventDefault()}
                                                onClick={() => {
                                                    setSupplierSearch(supplier)
                                                    setSelectedSupplier(supplier)
                                                    setSupplierOpen(false)
                                                }}
                                            >
                                                {supplier}
                                            </button>
                                        ))}
                                </div>
                            )}
                        </div>

                        <label>
                            Altvertrag gekündigt zum *
                            <input required type="date" />
                        </label>

                        <label>
                            Gewünschter Lieferbeginn *
                            <input required type="date" defaultValue={today} />
                        </label>

                        <p className="offer-hint">
                            Tarif und Verbrauch werden aus dem zuvor ausgewählten Angebot übernommen.
                        </p>
                    </section>

                    <section className="offer-card">
                        <h2>☑ Auftragsabschluss</h2>

                        <label className="offer-check">
                            <input type="checkbox" />
                            Rechnungsadresse ist abweichend
                        </label>

                        <hr />
                        <h3>Unterschrift</h3>

                        <label>
                            Datum der Unterschrift
                            <input type="date" defaultValue={today} />
                        </label>

                        <div className="offer-signature">
                            <strong>Digitale Unterschrift</strong>
                            <label className="offer-check">
                                <input
                                    type="checkbox"
                                    checked={digitalSignature}
                                    onChange={(event) => setDigitalSignature(event.target.checked)}
                                />
                                Kunde wünscht digitale Unterschrift
                            </label>
                            <span>
                                {digitalSignature
                                    ? 'Der Vertrag wird nach dem Speichern an den Kunden gesendet.'
                                    : 'Unterschrift wird vor Ort eingeholt.'}
                            </span>
                        </div>

                        <label className="offer-check">
                            <input type="checkbox" />
                            Kunde wünscht ausdrücklich eine Belieferung vor Ablauf der Widerrufsfrist.
                        </label>
                    </section>

                    <section
                        className="offer-card offer-actions"
                        style={{
                            display: 'flex',
                            flexDirection: 'row',
                            alignItems: 'flex-end',
                            gap: '16px',
                            padding: '20px',
                            flex: 1,
                            minHeight: 'auto',
                        }}
                    >
                        <button
                            type="button"
                            className="offer-secondary-button"
                            style={{ flex: 1, margin: 0 }}
                        >
                            Drucken / PDF
                        </button>
                        <button
                            type="submit"
                            className="offer-primary-button"
                            style={{ flex: 1, margin: 0 }}
                        >
                            {digitalSignature ? 'Abschluss mit Link →' : 'Auftrag lokal sichern'}
                        </button>
                    </section>
                </div>
            </form>
            </section>
        </div>
    )
}

export default OfferContract
