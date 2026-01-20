/**
 * User profile page with tabbed interface.
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useCurrentUser } from '../hooks/useAuth';
import { useInfiniteFavorites } from '../hooks/useUser';
import { ProfileForm } from '../components/user/ProfileForm';
import { PreferencesForm } from '../components/user/PreferencesForm';
import { AllergenSelector } from '../components/user/AllergenSelector';
import {
  Loader2,
  User,
  Settings,
  AlertTriangle,
  Heart,
  ChevronLeft,
  Clock,
  Users,
  ChefHat,
} from 'lucide-react';
import { ImageType } from '../types';

type TabId = 'profile' | 'preferences' | 'allergens' | 'favorites';

interface Tab {
  id: TabId;
  name: string;
  icon: typeof User;
}

const tabs: Tab[] = [
  { id: 'profile', name: 'Profile', icon: User },
  { id: 'preferences', name: 'Preferences', icon: Settings },
  { id: 'allergens', name: 'Allergens', icon: AlertTriangle },
  { id: 'favorites', name: 'Favorites', icon: Heart },
];

export const ProfilePage = (): JSX.Element => {
  const [activeTab, setActiveTab] = useState<TabId>('profile');
  const { data: user, isLoading: userLoading } = useCurrentUser();
  const {
    data: favoritesData,
    isLoading: favoritesLoading,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteFavorites(12);

  if (userLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
      </div>
    );
  }

  const allFavorites =
    favoritesData?.pages.flatMap((page) => page.items) ?? [];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link
                to="/"
                className="
                  text-gray-400 hover:text-gray-500 transition-colors
                "
              >
                <ChevronLeft className="h-6 w-6" />
              </Link>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Account Settings
                </h1>
                {user && (
                  <p className="mt-1 text-sm text-gray-500">
                    Logged in as {user.username}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="lg:grid lg:grid-cols-12 lg:gap-8">
          {/* Sidebar tabs */}
          <aside className="lg:col-span-3">
            <nav className="space-y-1">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;

                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      w-full group flex items-center px-3 py-2 text-sm font-medium
                      rounded-md transition-colors
                      ${
                        isActive
                          ? 'bg-blue-50 text-blue-700 hover:bg-blue-100'
                          : 'text-gray-700 hover:bg-gray-50'
                      }
                    `}
                  >
                    <Icon
                      className={`
                        flex-shrink-0 -ml-1 mr-3 h-5 w-5
                        ${
                          isActive
                            ? 'text-blue-600'
                            : 'text-gray-400 group-hover:text-gray-500'
                        }
                      `}
                    />
                    <span>{tab.name}</span>
                  </button>
                );
              })}
            </nav>
          </aside>

          {/* Main content */}
          <main className="mt-8 lg:mt-0 lg:col-span-9">
            {activeTab === 'profile' && <ProfileForm />}
            {activeTab === 'preferences' && <PreferencesForm />}
            {activeTab === 'allergens' && <AllergenSelector />}
            {activeTab === 'favorites' && (
              <div className="bg-white shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200">
                  <div className="flex items-center">
                    <Heart className="h-5 w-5 text-gray-400 mr-2" />
                    <h3 className="text-lg font-medium text-gray-900">
                      Favorite Recipes
                    </h3>
                  </div>
                </div>

                <div className="px-6 py-6">
                  {favoritesLoading ? (
                    <div className="flex justify-center py-12">
                      <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                    </div>
                  ) : allFavorites.length === 0 ? (
                    <div className="text-center py-12">
                      <Heart className="mx-auto h-12 w-12 text-gray-400" />
                      <h3 className="mt-2 text-sm font-medium text-gray-900">
                        No favorites yet
                      </h3>
                      <p className="mt-1 text-sm text-gray-500">
                        Start favoriting recipes to see them here.
                      </p>
                      <div className="mt-6">
                        <Link
                          to="/recipes"
                          className="
                            inline-flex items-center px-4 py-2 border
                            border-transparent shadow-sm text-sm font-medium
                            rounded-md text-white bg-blue-600 hover:bg-blue-700
                          "
                        >
                          Browse Recipes
                        </Link>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                        {allFavorites.map((recipe) => {
                          const mainImage = recipe.main_image;

                          return (
                            <Link
                              key={recipe.id}
                              to={`/recipes/${recipe.slug}`}
                              className="
                                group bg-white border border-gray-200 rounded-lg
                                overflow-hidden hover:shadow-lg transition-shadow
                              "
                            >
                              {/* Recipe image */}
                              {mainImage ? (
                                <div className="aspect-w-16 aspect-h-9 bg-gray-200">
                                  <img
                                    src={mainImage.url}
                                    alt={mainImage.alt_text || recipe.name}
                                    className="w-full h-48 object-cover"
                                  />
                                </div>
                              ) : (
                                <div className="w-full h-48 bg-gray-200 flex items-center justify-center">
                                  <ChefHat className="h-12 w-12 text-gray-400" />
                                </div>
                              )}

                              {/* Recipe info */}
                              <div className="p-4">
                                <h4 className="text-lg font-medium text-gray-900 group-hover:text-blue-600 line-clamp-2">
                                  {recipe.name}
                                </h4>
                                {recipe.description && (
                                  <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                                    {recipe.description}
                                  </p>
                                )}

                                {/* Recipe metadata */}
                                <div className="mt-3 flex items-center space-x-4 text-sm text-gray-500">
                                  {recipe.total_time_minutes && (
                                    <div className="flex items-center">
                                      <Clock className="h-4 w-4 mr-1" />
                                      <span>{recipe.total_time_minutes} min</span>
                                    </div>
                                  )}
                                  <div className="flex items-center">
                                    <Users className="h-4 w-4 mr-1" />
                                    <span>{recipe.servings} servings</span>
                                  </div>
                                </div>

                                {/* Nutrition summary */}
                                {recipe.nutrition_summary && (
                                  <div className="mt-3 flex items-center space-x-3 text-xs text-gray-600">
                                    {recipe.nutrition_summary.calories && (
                                      <span>
                                        {recipe.nutrition_summary.calories} cal
                                      </span>
                                    )}
                                    {recipe.nutrition_summary.protein_g && (
                                      <span>
                                        {recipe.nutrition_summary.protein_g}g protein
                                      </span>
                                    )}
                                  </div>
                                )}
                              </div>
                            </Link>
                          );
                        })}
                      </div>

                      {/* Load more button */}
                      {hasNextPage && (
                        <div className="mt-8 text-center">
                          <button
                            onClick={() => fetchNextPage()}
                            disabled={isFetchingNextPage}
                            className="
                              inline-flex items-center px-4 py-2 border
                              border-gray-300 shadow-sm text-sm font-medium
                              rounded-md text-gray-700 bg-white hover:bg-gray-50
                              disabled:opacity-50 disabled:cursor-not-allowed
                            "
                          >
                            {isFetchingNextPage ? (
                              <>
                                <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />
                                Loading...
                              </>
                            ) : (
                              'Load More'
                            )}
                          </button>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
};
