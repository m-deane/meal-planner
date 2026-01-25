import React from 'react';
import { Link } from 'react-router-dom';
import {
  UtensilsCrossed,
  Calendar,
  ShoppingCart,
  Heart,
  BarChart3,
  ChevronRight,
  Flame,
} from 'lucide-react';
import { useRecipes } from '../hooks/useRecipes';
import { useMealPlanStore } from '../store/mealPlanStore';
import { RecipeCard } from '../components/recipes';

interface QuickLinkProps {
  to: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  color: string;
}

const QuickLink: React.FC<QuickLinkProps> = ({ to, icon, title, description, color }) => (
  <Link
    to={to}
    className="group bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md hover:border-gray-300 transition-all"
  >
    <div className="flex items-start gap-4">
      <div className={`p-3 rounded-lg ${color}`}>
        {icon}
      </div>
      <div className="flex-1">
        <h3 className="font-semibold text-gray-900 group-hover:text-green-600 transition-colors">
          {title}
        </h3>
        <p className="text-sm text-gray-600 mt-1">{description}</p>
      </div>
      <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-green-600 transition-colors" />
    </div>
  </Link>
);

export const DashboardPage: React.FC = () => {
  const { data: recipesData, isLoading: recipesLoading } = useRecipes(
    { only_active: true },
    { page: 1, page_size: 6 }
  );
  const recipes = recipesData?.items ?? [];
  const { getTotalRecipes } = useMealPlanStore();
  const mealPlanCount = getTotalRecipes();

  const quickLinks: QuickLinkProps[] = [
    {
      to: '/recipes',
      icon: <UtensilsCrossed className="w-6 h-6 text-orange-600" />,
      title: 'Browse Recipes',
      description: 'Explore our collection of delicious recipes',
      color: 'bg-orange-50',
    },
    {
      to: '/meal-planner',
      icon: <Calendar className="w-6 h-6 text-blue-600" />,
      title: 'Meal Planner',
      description: 'Plan your weekly meals with drag & drop',
      color: 'bg-blue-50',
    },
    {
      to: '/nutrition',
      icon: <BarChart3 className="w-6 h-6 text-green-600" />,
      title: 'Nutrition Dashboard',
      description: 'Track your nutritional goals and macros',
      color: 'bg-green-50',
    },
    {
      to: '/shopping-list',
      icon: <ShoppingCart className="w-6 h-6 text-purple-600" />,
      title: 'Shopping List',
      description: 'Generate shopping lists from your meal plans',
      color: 'bg-purple-50',
    },
    {
      to: '/favorites',
      icon: <Heart className="w-6 h-6 text-red-600" />,
      title: 'Favorites',
      description: 'Access your saved favorite recipes',
      color: 'bg-red-50',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-green-600 to-green-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <h1 className="text-4xl font-bold mb-4">Welcome to Meal Planner</h1>
          <p className="text-green-100 text-lg max-w-2xl">
            Plan your meals, track nutrition, and generate shopping lists - all in one place.
            Start by browsing our recipe collection or jump straight into meal planning.
          </p>
          <div className="flex flex-wrap gap-4 mt-8">
            <Link
              to="/recipes"
              className="inline-flex items-center gap-2 px-6 py-3 bg-white text-green-700 font-semibold rounded-lg hover:bg-green-50 transition-colors"
            >
              <UtensilsCrossed className="w-5 h-5" />
              Browse Recipes
            </Link>
            <Link
              to="/meal-planner"
              className="inline-flex items-center gap-2 px-6 py-3 bg-green-500 text-white font-semibold rounded-lg hover:bg-green-400 transition-colors"
            >
              <Calendar className="w-5 h-5" />
              Start Planning
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-orange-50 rounded-lg">
                <UtensilsCrossed className="w-6 h-6 text-orange-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {recipesData?.total?.toLocaleString() ?? '4,500+'}
                </p>
                <p className="text-sm text-gray-600">Recipes Available</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-50 rounded-lg">
                <Calendar className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{mealPlanCount}</p>
                <p className="text-sm text-gray-600">Meals Planned</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-50 rounded-lg">
                <Flame className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">Healthy</p>
                <p className="text-sm text-gray-600">Nutrition Tracking</p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Links */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Access</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {quickLinks.map((link) => (
              <QuickLink key={link.to} {...link} />
            ))}
          </div>
        </div>

        {/* Featured Recipes */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Discover Recipes</h2>
            <Link
              to="/recipes"
              className="inline-flex items-center gap-1 text-green-600 hover:text-green-700 font-medium"
            >
              View All
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>

          {recipesLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div
                  key={i}
                  className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden animate-pulse"
                >
                  <div className="h-48 bg-gray-200" />
                  <div className="p-4 space-y-3">
                    <div className="h-4 bg-gray-200 rounded w-3/4" />
                    <div className="h-3 bg-gray-200 rounded w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : recipes.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recipes.map((recipe) => (
                <RecipeCard key={recipe.id} recipe={recipe} />
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-xl p-12 text-center border border-gray-200">
              <UtensilsCrossed className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No recipes yet</h3>
              <p className="text-gray-600 mb-4">
                Start by running the scraper to populate the database with recipes.
              </p>
              <div className="text-sm text-gray-500 bg-gray-50 rounded-lg p-4 font-mono">
                python -m src.cli scrape --limit 100
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
