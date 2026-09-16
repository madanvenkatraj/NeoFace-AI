with open('lib/firebase.ts', 'r') as f:
    content = f.read()

new_exports = """
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
"""

with open('lib/firebase.ts', 'w') as f:
    f.write(content + "\n" + new_exports)
