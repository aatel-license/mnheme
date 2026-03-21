import { NavLink } from 'react-router-dom';
import { useMemoryDB } from '../hooks/useMemoryDB';

const NAV_ITEMS = [
  { group: 'Memory',  items: [
    { to: '/',         icon: '>', label: 'Perceive' },
    { to: '/memories', icon: ':', label: 'Memories' },
    { to: '/brain',    icon: '*', label: 'Brain' },
  ]},
  { group: 'Explore', items: [
    { to: '/stats',    icon: '#', label: 'Stats' },
  ]},
  { group: 'System',  items: [
    { to: '/settings', icon: '@', label: 'Settings' },
  ]},
];

export default function Sidebar({ isOpen, onClose }) {
  const { count, listConcepts, revision } = useMemoryDB();
  const total    = count();
  const concepts = listConcepts().length;

  const handleNavClick = () => {
    // Close sidebar on mobile when a nav item is clicked
    if (onClose) onClose();
  };

  return (
    <aside className={`sidebar${isOpen ? ' open' : ''}`}>
      <div className="sidebar-header">
        <div className="logo-mark">
          <span className="logo-dot red" />
          <span className="logo-dot amber" />
          <span className="logo-dot green" />
        </div>
        <div className="logo-text">MNHEME</div>
        <div className="logo-sub">Memory Journal</div>
      </div>

      <nav className="nav-sections">
        {NAV_ITEMS.map(group => (
          <div key={group.group}>
            <div className="nav-group-label">{group.group}</div>
            {group.items.map(item => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => `nav-btn${isActive ? ' active' : ''}`}
                end={item.to === '/'}
                onClick={handleNavClick}
              >
                <span className="nav-icon">{item.icon}</span>
                {item.label}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="stat-pill">{total.toLocaleString()} memories</div>
        <div className="stat-pill">{concepts} concepts</div>
      </div>
    </aside>
  );
}
