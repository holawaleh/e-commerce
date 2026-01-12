"use client"
import React from 'react';
import { ShoppingCart, Package, BarChart3, Users, ArrowRight, CheckCircle, Zap, Shield, TrendingUp } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header/Navigation */}
      <nav className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <ShoppingCart className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold text-white">FleXBiz</span>
            </div>
            <div className="flex gap-4">
              <a 
                href="/login"
                className="px-4 py-2 text-slate-300 hover:text-white transition-colors"
              >
                Sign In
              </a>
              <a 
                href="/login"
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors"
              >
                Get Started
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 bg-blue-600/10 border border-blue-600/20 rounded-full px-4 py-2 mb-8">
            <Zap className="w-4 h-4 text-blue-400" />
            <span className="text-blue-400 text-sm font-semibold">Modern POS & Inventory Management</span>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Streamline Your Store
            <br />
            <span className="text-blue-400">Operations Today</span>
          </h1>
          
          <p className="text-xl text-slate-300 mb-10 max-w-2xl mx-auto">
            Professional Point of Sale and Inventory Management system designed for modern retail businesses. Process transactions quickly, track inventory in real-time, and grow your business.
          </p>
          
          <div className="flex gap-4 justify-center">
            <a 
              href="/login"
              className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold text-lg flex items-center gap-2 transition-colors"
            >
              Start Free Trial
              <ArrowRight className="w-5 h-5" />
            </a>
            <button className="px-8 py-4 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-semibold text-lg transition-colors">
              Watch Demo
            </button>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Everything You Need to Run Your Store
          </h2>
          <p className="text-lg text-slate-400">
            Powerful features designed for efficiency and growth
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* Feature 1 */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-blue-600 transition-colors">
            <div className="bg-blue-600 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <ShoppingCart className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Fast Checkout</h3>
            <p className="text-slate-400">
              Lightning-fast transaction processing with an intuitive interface. Keep lines moving and customers happy.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-blue-600 transition-colors">
            <div className="bg-blue-600 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <Package className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Real-Time Inventory</h3>
            <p className="text-slate-400">
              Automatic stock updates with every sale. Get low-stock alerts and never run out of bestsellers.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-blue-600 transition-colors">
            <div className="bg-blue-600 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Sales Analytics</h3>
            <p className="text-slate-400">
              Comprehensive reports and insights. Track performance, identify trends, and make data-driven decisions.
            </p>
          </div>

          {/* Feature 4 */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-blue-600 transition-colors">
            <div className="bg-blue-600 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <Users className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Multi-User Access</h3>
            <p className="text-slate-400">
              Manage multiple sales representatives with role-based permissions and activity tracking.
            </p>
          </div>

          {/* Feature 5 */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-blue-600 transition-colors">
            <div className="bg-blue-600 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Secure & Reliable</h3>
            <p className="text-slate-400">
              Bank-level security with cloud backup. Your data is always safe and accessible when you need it.
            </p>
          </div>

          {/* Feature 6 */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-blue-600 transition-colors">
            <div className="bg-blue-600 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Business Growth</h3>
            <p className="text-slate-400">
              Scale effortlessly as your business grows. From single store to multiple locations.
            </p>
          </div>
        </div>
      </div>

      {/* Benefits Section */}
      <div className="bg-slate-800 border-y border-slate-700 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
                Built for Sales Representatives
              </h2>
              <p className="text-lg text-slate-300 mb-8">
                FleXBiz is designed specifically for in-store sales teams. Every feature is crafted to help your staff work faster, serve customers better, and keep operations running smoothly.
              </p>
              
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
                  <div>
                    <h4 className="text-white font-semibold mb-1">Easy to Learn</h4>
                    <p className="text-slate-400">Train new staff in minutes, not hours</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
                  <div>
                    <h4 className="text-white font-semibold mb-1">Works Offline</h4>
                    <p className="text-slate-400">Continue selling even without internet</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
                  <div>
                    <h4 className="text-white font-semibold mb-1">24/7 Support</h4>
                    <p className="text-slate-400">Get help whenever you need it</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-2xl p-8">
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-white font-semibold">Today's Sales</span>
                  <TrendingUp className="w-5 h-5 text-white" />
                </div>
                <div className="text-4xl font-bold text-white mb-2">₦45,320</div>
                <div className="text-blue-100">+23% from yesterday</div>
              </div>
              
              <div className="mt-6 bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-white font-semibold">Items Sold</span>
                  <Package className="w-5 h-5 text-white" />
                </div>
                <div className="text-4xl font-bold text-white mb-2">127</div>
                <div className="text-blue-100">Across 34 transactions</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-2xl p-12 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Transform Your Store?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join hundreds of businesses using FleXBiz to streamline operations
          </p>
          <a 
            href="/login"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 rounded-lg font-semibold text-lg hover:bg-blue-50 transition-colors"
          >
            Get Started Now
            <ArrowRight className="w-5 h-5" />
          </a>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-700 bg-slate-900 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <ShoppingCart className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white">FleXBiz</span>
            </div>
            <p className="text-slate-400 text-sm">
              © 2026 FleXBiz. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}