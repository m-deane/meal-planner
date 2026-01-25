import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  Home,
  UtensilsCrossed,
  Calendar,
  ShoppingCart,
  Heart,
  User,
  Menu,
  X,
  BarChart3,
} from 'lucide-react';

interface NavItem {
  to: string;
  label: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: <Home className="w-5 h-5" aria-hidden="true" /> },
  { to: '/recipes', label: 'Recipes', icon: <UtensilsCrossed className="w-5 h-5" aria-hidden="true" /> },
  { to: '/meal-planner', label: 'Meal Planner', icon: <Calendar className="w-5 h-5" aria-hidden="true" /> },
  { to: '/nutrition', label: 'Nutrition', icon: <BarChart3 className="w-5 h-5" aria-hidden="true" /> },
  { to: '/shopping-list', label: 'Shopping List', icon: <ShoppingCart className="w-5 h-5" aria-hidden="true" /> },
  { to: '/favorites', label: 'Favorites', icon: <Heart className="w-5 h-5" aria-hidden="true" /> },
];

export const Navigation: React.FC = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();

  const isActive = (path: string): boolean => {
    return location.pathname === path || location.pathname.startsWith(`${path}/`);
  };

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <NavLink to="/dashboard" className="flex items-center gap-2" aria-label="Meal Planner home">
            <UtensilsCrossed className="w-8 h-8 text-green-600" aria-hidden="true" />
            <span className="text-xl font-bold text-gray-900">Meal Planner</span>
          </NavLink>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={`
                  flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors
                  ${isActive(item.to)
                    ? 'bg-green-50 text-green-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }
                `}
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </div>

          {/* Profile */}
          <div className="hidden md:flex items-center">
            <NavLink
              to="/profile"
              className={`
                flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors
                ${isActive('/profile')
                  ? 'bg-green-50 text-green-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }
              `}
            >
              <User className="w-5 h-5" aria-hidden="true" />
              Profile
            </NavLink>
          </div>

          {/* Mobile menu button */}
          <button
            type="button"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100"
            aria-label="Toggle menu"
            aria-expanded={isMobileMenuOpen}
            aria-controls="mobile-menu"
          >
            {isMobileMenuOpen ? (
              <X className="w-6 h-6" aria-hidden="true" />
            ) : (
              <Menu className="w-6 h-6" aria-hidden="true" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMobileMenuOpen && (
        <div id="mobile-menu" className="md:hidden border-t border-gray-200 bg-white">
          <div className="px-4 py-3 space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setIsMobileMenuOpen(false)}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors
                  ${isActive(item.to)
                    ? 'bg-green-50 text-green-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }
                `}
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
            <NavLink
              to="/profile"
              onClick={() => setIsMobileMenuOpen(false)}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors
                ${isActive('/profile')
                  ? 'bg-green-50 text-green-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }
              `}
            >
              <User className="w-5 h-5" aria-hidden="true" />
              Profile
            </NavLink>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navigation;
