import { Link } from 'react-router-dom'
import bannerImg from '../assets/banner.png'

function Dashboard({ user }) {
    const displayName =
        user?.first_name ||
        user?.email?.split('@')[0] ||
        'Benutzer'

    return (
        <div>
            <header className="dashboard-header">
                <div>
                    <h1>Hallo, {displayName}!</h1>
                    <p>Willkommen in Ihrem persönlichen Bereich.</p>
                </div>

                <div className="header-actions">
                    <button className="notification-button">
                        ♧
                        <span>3</span>
                    </button>

                    <div className="header-user">♙⌄</div>

                    <Link to="/contracts/new" className="new-contract-button">
                        <span>＋</span>
                        Neuer Vertrag
                    </Link>
                </div>
            </header>

            <section className="kpi-grid">
                <KpiCard title="Gesamtverträge" value="—" footer="Gesamt" icon="▤" />
                <KpiCard title="In Bearbeitung" value="—" footer="Verträge" icon="◷" />
                <KpiCard title="Erwartete Provision" value="—" footer="Aktuell" icon="€" />
                <KpiCard title="Ausgezahlte Provision" value="—" footer="Gesamt" icon="▣" />
            </section>

            <section className="dashboard-grid">
                <div className="left-column">
                    <div className="panel provision-panel">
                        <div className="panel-title-row">
                            <h2>Provisionen Übersicht</h2>
                            <button className="period-button">Dieses Jahr⌄</button>
                        </div>

                        <div className="chart-legend">
                            <span>
                                <i className="legend-dot light" />
                                Erwartete Provision
                            </span>

                            <span>
                                <i className="legend-dot dark" />
                                Ausbezahlte Provision
                            </span>
                        </div>

                        <div className="chart">
                            <div className="chart-y-label y1">10.000 €</div>
                            <div className="chart-y-label y2">8.000 €</div>
                            <div className="chart-y-label y3">6.000 €</div>
                            <div className="chart-y-label y4">4.000 €</div>
                            <div className="chart-y-label y5">2.000 €</div>
                            <div className="chart-y-label y6">0 €</div>

                            <div className="chart-area">
                                <div className="grid-line line1" />
                                <div className="grid-line line2" />
                                <div className="grid-line line3" />
                                <div className="grid-line line4" />
                                <div className="grid-line line5" />

                                <div className="chart-placeholder">
                                    Provisionsdaten werden geladen
                                </div>
                            </div>

                            <div className="months">
                                <span>Jan</span>
                                <span>Feb</span>
                                <span>Mär</span>
                                <span>Apr</span>
                                <span>Mai</span>
                                <span>Jun</span>
                                <span>Jul</span>
                                <span>Aug</span>
                                <span>Sep</span>
                                <span>Okt</span>
                                <span>Nov</span>
                                <span>Dez</span>
                            </div>
                        </div>
                    </div>

                    <div className="panel contracts-panel">
                        <div className="panel-title-row">
                            <h2>Letzte Verträge</h2>
                            <button className="text-button">Alle anzeigen</button>
                        </div>

                        <div className="contracts-table">
                            <div className="table-row table-header">
                                <span>Vertragsnummer</span>
                                <span>Kunde</span>
                                <span>Tarif</span>
                                <span>Abschlussdatum</span>
                                <span>Provision</span>
                                <span>Status</span>
                                <span>Aktionen</span>
                            </div>

                            <div className="table-empty">
                                Noch keine Vertragsdaten geladen.
                            </div>
                        </div>

                        <button className="all-contracts">
                            Alle Verträge anzeigen
                        </button>
                    </div>
                </div>

                <div className="right-column">
                    <div className="panel status-panel">
                        <h2>Vertragsstatus</h2>

                        <div className="status-content">
                            <div className="donut">
                                <div className="donut-center">
                                    <strong>—</strong>
                                    <span>Gesamt</span>
                                </div>
                            </div>

                            <div className="status-list">
                                <StatusItem className="status-new" label="Neu" value="—" />
                                <StatusItem className="status-review" label="In Prüfung" value="—" />
                                <StatusItem className="status-progress" label="In Bearbeitung" value="—" />
                                <StatusItem className="status-confirmed" label="Bestätigt" value="—" />
                                <StatusItem className="status-paid" label="Ausbezahlt" value="—" />
                                <StatusItem className="status-rejected" label="Abgelehnt" value="—" />
                            </div>
                        </div>
                    </div>

                    <div className="panel news-panel">
                        <div className="panel-title-row">
                            <h2>Aktuelle Nachrichten</h2>
                            <button className="text-button">Alle anzeigen</button>
                        </div>

                        <NewsItem
                            icon="◉"
                            title="Willkommen im Gigawatt Portal"
                            text="Alle wichtigen Informationen finden Sie direkt in Ihrem persönlichen Bereich."
                        />

                        <NewsItem
                            icon="▤"
                            title="System Update"
                            text="Das Partnerportal wird laufend erweitert und verbessert."
                        />
                    </div>

                    <div className="green-banner">
                        <img
                            src={bannerImg}
                            alt="Gigawatt Solution"
                            className="green-banner-image"
                        />
                    </div>
                </div>
            </section>
        </div>
    )
}

function KpiCard({ title, value, footer, icon }) {
    return (
        <div className="kpi-card">
            <div>
                <span className="kpi-title">{title}</span>
                <strong className="kpi-value">{value}</strong>
                <span className="kpi-footer">{footer}</span>
            </div>

            <div className="kpi-icon">{icon}</div>
        </div>
    )
}

function StatusItem({ className, label, value }) {
    return (
        <div className="status-item">
            <span className={`status-dot ${className}`} />
            <span>{label}</span>
            <strong>{value}</strong>
        </div>
    )
}

function NewsItem({ icon, title, text }) {
    return (
        <div className="news-item">
            <div className="news-icon">{icon}</div>

            <div>
                <strong>{title}</strong>
                <p>{text}</p>
            </div>
        </div>
    )
}

export default Dashboard