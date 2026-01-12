"use client"
import React, { useState } from 'react';
import { ShoppingCart, Package, BarChart3, Users, CheckCircle, TrendingUp } from 'lucide-react';

export default function FleXBizAuth() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    storeName: '',
    fullName: ''
  });

 const handleSubmit = () => {
  console.log('Form submitted:', formData);
  
  if (isLogin) {
    // Login - go directly to dashboard
    window.location.href = '/dashboard';
  } else {
    // Signup - go to business selector
    window.location.href = '/select-business';
  }
};

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex">
      {/* Information Section */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 to-blue-800 p-12 flex-col justify-between text-white">
        <div>
          <div className="flex items-center gap-3 mb-12">
            <div className="bg-white p-2 rounded-lg">
              <ShoppingCart className="w-8 h-8 text-blue-600" />
            </div>
            <h1 className="text-4xl font-bold">FleXBiz</h1>
          </div>

          <h2 className="text-3xl font-bold mb-6">
            Streamline Your Store Operations
          </h2>
          <p className="text-lg text-blue-100 mb-12">
            Professional POS and Inventory Management designed for modern retail businesses.
            Process transactions quickly, track inventory in real-time, and grow your business.
          </p>

          <div className="space-y-6">
            <div className="flex items-start gap-4">
              <div className="bg-blue-700 p-3 rounded-lg">
                <Package className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold text-xl mb-2">Real-Time Inventory Tracking</h3>
                <p className="text-blue-100">
                  Automatically update stock levels with every sale. Never run out of popular items or overstock slow movers.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="bg-blue-700 p-3 rounded-lg">
                <BarChart3 className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold text-xl mb-2">Sales Analytics & Reports</h3>
                <p className="text-blue-100">
                  Track daily sales, identify trends, and make data-driven decisions to boost your revenue.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="bg-blue-700 p-3 rounded-lg">
                <Users className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold text-xl mb-2">Multi-User Access</h3>
                <p className="text-blue-100">
                  Manage multiple sales representatives with role-based permissions and activity tracking.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="bg-blue-700 p-3 rounded-lg">
                <TrendingUp className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold text-xl mb-2">Fast Checkout Experience</h3>
                <p className="text-blue-100">
                  Intuitive interface designed for speed. Process transactions in seconds and keep lines moving.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-6 text-sm text-blue-100">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            <span>Secure & Reliable</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            <span>24/7 Support</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            <span>Cloud-Based</span>
          </div>
        </div>
      </div>

      {/* Auth Form Section */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden flex items-center gap-3 mb-8 justify-center">
            <div className="bg-blue-600 p-2 rounded-lg">
              <ShoppingCart className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-white">FleXBiz</h1>
          </div>

          <div className="bg-slate-800 rounded-2xl shadow-2xl p-8">
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-white mb-2">
                {isLogin ? 'Welcome Back' : 'Create Account'}
              </h2>
              <p className="text-slate-400">
                {isLogin 
                  ? 'Sign in to access your POS dashboard' 
                  : 'Start managing your store efficiently'}
              </p>
            </div>

            <div onSubmit={handleSubmit} className="space-y-5">
              {!isLogin && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Store Name
                    </label>
                    <input
                      type="text"
                      name="storeName"
                      value={formData.storeName}
                      onChange={handleChange}
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Your Store Name"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Full Name
                    </label>
                    <input
                      type="text"
                      name="fullName"
                      value={formData.fullName}
                      onChange={handleChange}
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="John Doe"
                      required
                    />
                  </div>
                </>
              )}

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="you@example.com"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="••••••••"
                  required
                />
              </div>

              {isLogin && (
                <div className="flex items-center justify-between">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      className="w-4 h-4 rounded border-slate-600 bg-slate-700 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-slate-300">Remember me</span>
                  </label>
                  <a href="#" className="text-sm text-blue-400 hover:text-blue-300">
                    Forgot password?
                  </a>
                </div>
              )}

              <button
                onClick={handleSubmit}
                type="button"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
              >
                {isLogin ? 'Sign In' : 'Create Account'}
                <ShoppingCart className="w-5 h-5" />
              </button>
            </div>

            <div className="mt-6 text-center">
              <p className="text-slate-400">
                {isLogin ? "Don't have an account? " : "Already have an account? "}
                <button
                  onClick={() => setIsLogin(!isLogin)}
                  className="text-blue-400 hover:text-blue-300 font-semibold"
                >
                  {isLogin ? 'Sign Up' : 'Sign In'}
                </button>
              </p>
            </div>
          </div>

          {/* Mobile Features Preview */}
          <div className="lg:hidden mt-8 text-center">
            <p className="text-slate-400 text-sm">
              Trusted by retail businesses for fast, reliable POS operations
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}