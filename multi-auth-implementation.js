// Multi-Provider Authentication System for HardCard Ecosystem
// Supports Google, Microsoft, Apple, and Meta authentication

import { initializeApp } from 'firebase/app';
import { 
  getAuth, 
  GoogleAuthProvider, 
  OAuthProvider, 
  FacebookAuthProvider,
  signInWithPopup,
  onAuthStateChanged 
} from 'firebase/auth';

// Firebase configuration
const firebaseConfig = {
  apiKey: process.env.FIREBASE_API_KEY,
  authDomain: process.env.FIREBASE_AUTH_DOMAIN,
  projectId: process.env.FIREBASE_PROJECT_ID,
  storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.FIREBASE_APP_ID
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Owner configuration - CHANGE THIS TO YOUR EMAIL/IDS
const OWNER_CONFIG = {
  emails: ['dallas@hardcard.co'], // Add your email(s)
  allowedIds: {
    google: ['your-google-user-id'],
    microsoft: ['your-microsoft-user-id'],
    apple: ['your-apple-user-id'],
    facebook: ['your-facebook-user-id']
  }
};

// Authentication providers
const providers = {
  google: new GoogleAuthProvider(),
  microsoft: new OAuthProvider('microsoft.com'),
  apple: new OAuthProvider('apple.com'),
  facebook: new FacebookAuthProvider()
};

// Configure providers
providers.google.addScope('email');
providers.google.addScope('profile');

providers.microsoft.setCustomParameters({
  prompt: 'select_account'
});

providers.apple.addScope('email');
providers.apple.addScope('name');

providers.facebook.addScope('email');
providers.facebook.addScope('public_profile');

// Authentication functions
export const signInWithProvider = async (providerName) => {
  try {
    const provider = providers[providerName];
    if (!provider) {
      throw new Error(`Provider ${providerName} not supported`);
    }
    
    const result = await signInWithPopup(auth, provider);
    const user = result.user;
    
    // Check if user is owner
    const isOwner = checkIfOwner(user);
    
    // Store user data
    await storeUserData(user, providerName, isOwner);
    
    return { user, isOwner };
  } catch (error) {
    console.error('Authentication error:', error);
    throw error;
  }
};

// Check if user is the owner
const checkIfOwner = (user) => {
  // Check by email
  if (OWNER_CONFIG.emails.includes(user.email)) {
    return true;
  }
  
  // Check by provider-specific ID
  const providerId = user.providerData[0]?.providerId;
  const uid = user.providerData[0]?.uid;
  
  if (providerId && uid) {
    const providerKey = providerId.replace('.com', '');
    return OWNER_CONFIG.allowedIds[providerKey]?.includes(uid) || false;
  }
  
  return false;
};

// Store user data in Firestore
const storeUserData = async (user, provider, isOwner) => {
  const db = getFirestore();
  const userRef = doc(db, 'users', user.uid);
  
  const userData = {
    uid: user.uid,
    email: user.email,
    displayName: user.displayName,
    photoURL: user.photoURL,
    provider: provider,
    isOwner: isOwner,
    createdAt: new Date(),
    lastLogin: new Date()
  };
  
  await setDoc(userRef, userData, { merge: true });
  
  // Add to waiting list if not owner
  if (!isOwner) {
    await addToWaitingList(user, provider);
  }
};

// Waiting list management
const addToWaitingList = async (user, provider) => {
  const db = getFirestore();
  const waitingListRef = collection(db, 'waitingList');
  
  // Check if already on waiting list
  const q = query(waitingListRef, where('email', '==', user.email));
  const existing = await getDocs(q);
  
  if (existing.empty) {
    const position = await getNextPosition();
    
    await addDoc(waitingListRef, {
      email: user.email,
      name: user.displayName,
      authProvider: provider,
      authId: user.uid,
      signupDate: new Date(),
      tier: 'free',
      precommitment: {
        plan: 'free',
        monthlyValue: 0
      },
      position: position,
      bracket: 'standard',
      status: 'waiting'
    });
  }
};

// Get next position in waiting list
const getNextPosition = async