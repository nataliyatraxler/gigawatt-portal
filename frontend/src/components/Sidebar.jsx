import { NavLink } from 'react-router-dom'
import logo from '../assets/gigawatt-logo.png'
function Sidebar({ user, onLogout }) {
    const roleNames = {
        superadmin: 'Superadmin',
        agent: 'Vertriebspartner',
        lieferant: 'Lieferant',
    }

    const displayName =
        `${user?.first_name || ''} ${user?.last_name || ''}`.trim() ||
        user?.email ||
        'Benutzer'

    const initials =
        `${user?.first_name?.[0] || ''}${user?.last_name?.[0] || ''}` ||
        displayName.substring(0, 2)

    const menuItems = [
        {
            path: '/',
            icon: '⌂',
            label: 'Dashboard',
        },
        {
            path: '/contracts',
            icon: '▤',
            label: 'Verträge',
        },
        {
            path: '/contracts/new',
            icon: '＋',
            label: 'Neuer Vertrag',
        },
        {
            path: '/customers',
            icon: '♙',
            label: 'Kunden',
        },
        {
            path: '/commissions',
            icon: '€',
            label: 'Provisionen',
        },
        {
            path: '/payments',
            icon: '▣',
            label: 'Auszahlungen',
        },
        {
            path: '/documents',
            icon: '□',
            label: 'Dokumente',
        },
        {
            path: '/reports',
            icon: '▥',
            label: 'Berichte',
        },
        {
            path: '/messages',
            icon: '✉',
            label: 'Nachrichten',
        },
        {
            path: '/settings',
            icon: '⚙',
            label: 'Einstellungen',
        },
    ]

    return (
        <aside className="sidebar">
            <div className="portal-logo">
                <img
                    src={logo}
                    alt="Gigawatt Solution"
                    className="portal-logo-image"
                />
            </div>

            <div className="sidebar-user">
                <div className="sidebar-avatar">
                    {initials.toUpperCase()}
                </div>

                <div className="sidebar-user-info">
                    <strong>{displayName}</strong>

                    <span>
                        {roleNames[user?.role] || user?.role}
                    </span>
                </div>

                <span className="sidebar-chevron">⌄</span>
            </div>

            <nav className="sidebar-menu">
                {menuItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        end={item.path === '/'}
                        className={({ isActive }) =>
                            `menu-item ${isActive ? 'active' : ''}`
                        }
                    >
                        <span className="menu-icon">
                            {item.icon}
                        </span>

                        {item.label}
                    </NavLink>
                ))}
            </nav>

            <button
                className="sidebar-logout"
                onClick={onLogout}
            >
                <span>↪</span>
                Abmelden
            </button>

            <div className="support-box">
                <div className="support-icon">◉</div>

                <div>
                    <strong>Haben Sie Fragen?</strong>
                    <span>Support kontaktieren</span>
                </div>
            </div>
        </aside>
    )
}

export default Sidebar