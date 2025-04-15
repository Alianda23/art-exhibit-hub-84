
import React, { createContext, useContext, useState, useEffect } from "react";
import { User } from "@/types";
import { 
  loginUser, 
  loginAdmin, 
  registerUser, 
  logout as apiLogout, 
  isAuthenticated as checkIsAuthenticated,
  isAdmin as checkIsAdmin
} from "@/services/api";

type AuthContextType = {
  currentUser: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  adminLogin: (email: string, password: string) => Promise<boolean>;
  signup: (name: string, email: string, password: string, phone: string) => Promise<boolean>;
  logout: () => void;
  isAdmin: boolean;
  isAuthenticated: boolean;
};

const AuthContext = createContext<AuthContextType>({
  currentUser: null,
  login: async () => false,
  adminLogin: async () => false,
  signup: async () => false,
  logout: () => {},
  isAdmin: false,
  isAuthenticated: false,
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [isUserAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  // Check if user is already logged in
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const isAuthenticated = checkIsAuthenticated();
        if (isAuthenticated) {
          const userName = localStorage.getItem('userName') || '';
          const userId = localStorage.getItem('userId') || localStorage.getItem('adminId') || '';
          const userIsAdmin = localStorage.getItem('isAdmin') === 'true';
          
          console.log("Auth check:", { 
            userName, 
            userId, 
            isAdmin: userIsAdmin,
            token: localStorage.getItem('token')?.substring(0, 20) + '...',
            localStorageIsAdmin: localStorage.getItem('isAdmin')
          });
          
          // Create a basic user object from localStorage
          setCurrentUser({
            id: userId,
            name: userName,
            email: '',  // We don't store sensitive info in localStorage
            isAdmin: userIsAdmin,
          });
          
          setIsAdmin(userIsAdmin);
          setIsAuthenticated(true);
        } else {
          console.log("User is not authenticated");
          setCurrentUser(null);
          setIsAdmin(false);
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error("Authentication check error:", error);
        setCurrentUser(null);
        setIsAdmin(false);
        setIsAuthenticated(false);
      }
    };
    
    checkAuth();
  }, []);

  // Regular user login
  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      console.log('AuthContext: Attempting user login', { email });
      const response = await loginUser({ email, password });
      
      if (response.error) {
        console.log('AuthContext: Login failed', response.error);
        return false;
      }
      
      // Set user state from response
      setCurrentUser({
        id: response.user_id?.toString() || '',
        name: response.name || '',
        email: email,
        isAdmin: false,
      });
      
      setIsAdmin(false);
      setIsAuthenticated(true);
      console.log('AuthContext: Login successful', { name: response.name, isAdmin: false });
      return true;
    } catch (error) {
      console.error("Login error:", error);
      throw error; // Rethrow to handle in component
    }
  };

  // Admin login
  const adminLogin = async (email: string, password: string): Promise<boolean> => {
    try {
      console.log('AuthContext: Attempting admin login', { email });
      const response = await loginAdmin({ email, password });
      
      if (response.error) {
        console.log('AuthContext: Admin login failed', response.error);
        return false;
      }
      
      // Set admin user state
      setCurrentUser({
        id: response.admin_id?.toString() || '',
        name: response.name || '',
        email: email,
        isAdmin: true,
      });
      
      setIsAdmin(true);
      setIsAuthenticated(true);
      console.log('AuthContext: Admin login successful', { 
        name: response.name, 
        isAdmin: true,
        token: localStorage.getItem('token')?.substring(0, 20) + '...'
      });
      return true;
    } catch (error) {
      console.error("Admin login error:", error);
      throw error; // Rethrow to handle in component
    }
  };
  
  // User signup
  const signup = async (name: string, email: string, password: string, phone: string): Promise<boolean> => {
    try {
      console.log('AuthContext: Attempting signup', { name, email });
      const response = await registerUser({ name, email, password, phone });
      
      if (response.error) {
        console.log('AuthContext: Signup failed', response.error);
        return false;
      }
      
      // Set user state after successful registration
      setCurrentUser({
        id: response.user_id?.toString() || '',
        name: name,
        email: email,
        isAdmin: false,
      });
      
      setIsAdmin(false);
      setIsAuthenticated(true);
      console.log('AuthContext: Signup successful');
      return true;
    } catch (error) {
      console.error("Signup error:", error);
      throw error; // Rethrow to handle in component
    }
  };

  // Logout
  const logout = () => {
    apiLogout();
    setCurrentUser(null);
    setIsAdmin(false);
    setIsAuthenticated(false);
    console.log('AuthContext: User logged out');
  };

  const value = {
    currentUser,
    login,
    adminLogin,
    signup,
    logout,
    isAdmin,
    isAuthenticated: isUserAuthenticated,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
