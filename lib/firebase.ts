import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from 'firebase/auth';
import { getFirestore, doc, setDoc, getDoc, collection, getDocs, onSnapshot } from 'firebase/firestore';
import firebaseConfig from '../firebase-applet-config.json';

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app, firebaseConfig.firestoreDatabaseId);
export const auth = getAuth(app);

const provider = new GoogleAuthProvider();

export const signIn = async () => {
  try {
    await signInWithPopup(auth, provider);
  } catch (error) {
    console.error("Error signing in with Google", error);
  }
};

export const logOut = async () => {
  try {
    await signOut(auth);
  } catch (error) {
    console.error("Error signing out", error);
  }
};

// Error handler based on the Firebase skill guidelines
enum OperationType {
  CREATE = 'create',
  UPDATE = 'update',
  DELETE = 'delete',
  LIST = 'list',
  GET = 'get',
  WRITE = 'write',
}

interface FirestoreErrorInfo {
  error: string;
  operationType: OperationType;
  path: string | null;
  authInfo: {
    userId?: string | null;
    email?: string | null;
    emailVerified?: boolean | null;
    isAnonymous?: boolean | null;
    tenantId?: string | null;
    providerInfo?: {
      providerId?: string | null;
      email?: string | null;
    }[];
  }
}

export function handleFirestoreError(error: unknown, operationType: OperationType, path: string | null) {
  const errInfo: FirestoreErrorInfo = {
    error: error instanceof Error ? error.message : String(error),
    authInfo: {
      userId: auth.currentUser?.uid,
      email: auth.currentUser?.email,
      emailVerified: auth.currentUser?.emailVerified,
      isAnonymous: auth.currentUser?.isAnonymous,
      tenantId: auth.currentUser?.tenantId,
      providerInfo: auth.currentUser?.providerData?.map(provider => ({
        providerId: provider.providerId,
        email: provider.email,
      })) || []
    },
    operationType,
    path
  }
  console.error('Firestore Error: ', JSON.stringify(errInfo));
  throw new Error(JSON.stringify(errInfo));
}

// Helpers for syncing data
export const saveUserPreferences = async (userId: string, preferences: any) => {
  const path = `users/${userId}`;
  try {
    await setDoc(doc(db, 'users', userId), {
      uid: userId,
      email: auth.currentUser?.email || '',
      displayName: auth.currentUser?.displayName || '',
      preferences,
      updatedAt: Date.now()
    }, { merge: true });
  } catch (error) {
    handleFirestoreError(error, OperationType.WRITE, path);
  }
};

export const getUserPreferences = async (userId: string) => {
  const path = `users/${userId}`;
  try {
    const d = await getDoc(doc(db, 'users', userId));
    return d.exists() ? d.data().preferences : null;
  } catch (error) {
    handleFirestoreError(error, OperationType.GET, path);
    return null;
  }
};

export const saveProjectHistory = async (userId: string, projectId: string, projectData: any) => {
  const path = `users/${userId}/exportSettings/${projectId}`;
  try {
    await setDoc(doc(db, 'users', userId, 'exportSettings', projectId), {
      ...projectData,
      id: projectId,
      userId,
      updatedAt: Date.now()
    }, { merge: true });
  } catch (error) {
    handleFirestoreError(error, OperationType.WRITE, path);
  }
};

export const getProjectHistory = async (userId: string) => {
  const path = `users/${userId}/exportSettings`;
  try {
    const snap = await getDocs(collection(db, 'users', userId, 'exportSettings'));
    return snap.docs.map(d => d.data());
  } catch (error) {
    handleFirestoreError(error, OperationType.LIST, path);
    return [];
  }
};


// Drive picker helpers
let cachedAccessToken: string | null = null;

export const googleSignIn = async () => {
  try {
    const provider = new GoogleAuthProvider();
    provider.addScope('https://www.googleapis.com/auth/drive.readonly');
    const result = await signInWithPopup(auth, provider);
    const credential = GoogleAuthProvider.credentialFromResult(result);
    if (credential && credential.accessToken) {
      cachedAccessToken = credential.accessToken;
      return { accessToken: credential.accessToken, user: result.user };
    }
    return { user: result.user };
  } catch (error) {
    console.error("Error signing in with Google for Drive", error);
    return null;
  }
};

export const getAccessToken = async () => {
  return cachedAccessToken;
};
