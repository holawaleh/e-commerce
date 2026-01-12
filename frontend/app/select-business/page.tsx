"use client"
import React, { useState } from 'react';
import { 
  ShoppingCart, 
  Coffee, 
  ShoppingBag, 
  Croissant,
  Store,
  Shirt,
  Heart,
  Monitor,
  Smartphone,
  Car,
  Scissors,
  Hotel,
  ArrowRight,
  Check
} from 'lucide-react';

interface BusinessType {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  color: string;
}

export default function BusinessSelector() {
  const [selectedBusiness, setSelectedBusiness] = useState<string | null>(null);

  const businessTypes: BusinessType[] = [
    {
      id: 'restaurant',
      name: 'Restaurant',
      icon: <Coffee className="w-10 h-10" />,
      description: 'Full-service dining',
      color: 'from-orange-500 to-red-500'
    },
    {
      id: 'cafe',
      name: 'Cafe',
      icon: <Coffee className="w-10 h-10" />,
      description: 'Coffee & snacks',
      color: 'from-amber-500 to-orange-500'
    },
    {
      id: 'grocery',
      name: 'Grocery',
      icon: <ShoppingBag className="w-10 h-10" />,
      description: 'Food & essentials',
      color: 'from-green-500 to-emerald-500'
    },
    {
      id: 'bakery',
      name: 'Bakery',
      icon: <Croissant className="w-10 h-10" />,
      description: 'Fresh baked goods',
      color: 'from-yellow-500 to-amber-500'
    },
    {
      id: 'ecommerce',
      name: 'E-commerce',
      icon: <ShoppingCart className="w-10 h-10" />,
      description: 'Online retail store',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      id: 'apparel',
      name: 'Apparel',
      icon: <Shirt className="w-10 h-10" />,
      description: 'Clothing & fashion',
      color: 'from-purple-500 to-pink-500'
    },
    {
      id: 'health',
      name: 'Health',
      icon: <Heart className="w-10 h-10" />,
      description: 'Pharmacy & wellness',
      color: 'from-red-500 to-pink-500'
    },
    {
      id: 'electronics',
      name: 'Electronics',
      icon: <Monitor className="w-10 h-10" />,
      description: 'Tech & gadgets',
      color: 'from-indigo-500 to-blue-500'
    },
    {
      id: 'digital',
      name: 'Digital Products',
      icon: <Smartphone className="w-10 h-10" />,
      description: 'Software & services',
      color: 'from-cyan-500 to-teal-500'
    },
    {
      id: 'rental',
      name: 'Rental',
      icon: <Car className="w-10 h-10" />,
      description: 'Equipment & vehicles',
      color: 'from-slate-500 to-gray-500'
    },
    {
      id: 'salon',
      name: 'Salon',
      icon: <Scissors className="w-10 h-10" />,
      description: 'Beauty & grooming',
      color: 'from-pink-500 to-rose-500'
    },
    {
      id: 'hotel',
      name: 'Hotel',
      icon: <Hotel className="w-10 h-10" />,
      description: 'Hospitality & lodging',
      color: 'from-blue-500 to-purple-500'
    }
  ];

  const handleContinue = () => {
    if (selectedBusiness) {
      console.log('Selected business:', selectedBusiness);
      // Navigate to dashboard with business type
      window.location.href = `/dashboard?type=${selectedBusiness}`;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="bg-blue-600 p-3 rounded-xl">
              <Store className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white">FleXBiz</h1>
          </div>
          
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Choose Your Business Type
          </h2>
          <p className="text-xl text-slate-300 max-w-2xl mx-auto">
            Select the category that best describes your business. We'll customize your dashboard and features accordingly.
          </p>
        </div>

        {/* Business Type Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-8">
          {businessTypes.map((business) => (
            <button
              key={business.id}
              onClick={() => setSelectedBusiness(business.id)}
              className={`relative group bg-slate-800 border-2 rounded-2xl p-6 transition-all duration-200 hover:scale-105 ${
                selectedBusiness === business.id
                  ? 'border-blue-500 shadow-lg shadow-blue-500/20'
                  : 'border-slate-700 hover:border-slate-600'
              }`}
            >
              {/* Selection Indicator */}
              {selectedBusiness === business.id && (
                <div className="absolute -top-2 -right-2 bg-blue-500 rounded-full p-1.5">
                  <Check className="w-4 h-4 text-white" />
                </div>
              )}

              {/* Icon with Gradient Background */}
              <div className={`bg-gradient-to-br ${business.color} rounded-xl p-4 mb-4 mx-auto w-fit text-white`}>
                {business.icon}
              </div>

              {/* Business Name */}
              <h3 className="text-lg font-semibold text-white mb-1">
                {business.name}
              </h3>
              
              {/* Description */}
              <p className="text-sm text-slate-400">
                {business.description}
              </p>
            </button>
          ))}
        </div>

        {/* Continue Button */}
        <div className="flex justify-center">
          <button
            onClick={handleContinue}
            disabled={!selectedBusiness}
            className={`flex items-center gap-3 px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-200 ${
              selectedBusiness
                ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-500/30 hover:scale-105'
                : 'bg-slate-700 text-slate-400 cursor-not-allowed'
            }`}
          >
            Continue to Dashboard
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>

        {/* Skip Option */}
        <div className="text-center mt-6">
          <button 
            onClick={() => window.location.href = '/dashboard'}
            className="text-slate-400 hover:text-slate-300 text-sm transition-colors"
          >
            Skip for now, I'll choose later
          </button>
        </div>

        {/* Info Box */}
        <div className="mt-12 bg-blue-600/10 border border-blue-600/20 rounded-xl p-6 max-w-2xl mx-auto">
          <div className="flex items-start gap-4">
            <div className="bg-blue-600 p-2 rounded-lg flex-shrink-0">
              <Store className="w-5 h-5 text-white" />
            </div>
            <div>
              <h4 className="text-white font-semibold mb-2">Why choose a business type?</h4>
              <p className="text-blue-100 text-sm leading-relaxed">
                FleXBiz customizes your dashboard, inventory categories, and reporting based on your business type. 
                You'll get industry-specific features and workflows that make managing your store easier. 
                Don't worry - you can change this later in settings.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}