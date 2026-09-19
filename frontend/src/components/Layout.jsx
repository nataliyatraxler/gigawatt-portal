import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'

function Layout({ user, onLogout }) {
    return (
        <div className="portal">
            <Sidebar
                user={user}
                onLogout={onLogout}
            />

            <main className="main-content">
                <Outlet />
            </main>
        </div>
    )
}

export default Layout