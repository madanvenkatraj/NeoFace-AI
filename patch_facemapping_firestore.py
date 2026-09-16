import sys

with open("components/FaceMappingStudio.tsx", "r") as f:
    code = f.read()

import_insert = "import ProgressBar from './ProgressBar';"
import_replacement = "import ProgressBar from './ProgressBar';\nimport { db, auth } from '../lib/firebase';\nimport { doc, setDoc } from 'firebase/firestore';"

code = code.replace(import_insert, import_replacement)

success_block = """        } else if (data.state === 'SUCCESS') {
          clearInterval(interval);
          setProgress(100);
          setStatusMsg("Completed");
          setResultPath(data.result.output_path);
          if (data.result.metrics) {
            setJobMetrics(data.result.metrics);
          }
          setJobId(null);"""

success_replacement = """        } else if (data.state === 'SUCCESS') {
          clearInterval(interval);
          setProgress(100);
          setStatusMsg("Completed");
          
          const finalResultPath = data.result.output_path;
          setResultPath(finalResultPath);
          
          if (data.result.metrics) {
            setJobMetrics(data.result.metrics);
          }
          setJobId(null);

          if (auth.currentUser) {
            const uid = auth.currentUser.uid;
            const historyId = Date.now().toString() + Math.random().toString(36).substring(2, 9);
            const historyRef = doc(db, 'users', uid, 'swapHistory', historyId);
            setDoc(historyRef, {
              id: historyId,
              userId: uid,
              resultUrl: finalResultPath,
              isVideo: isVideo,
              createdAt: Date.now(),
              qualityMode: qualityMode,
              facesSwapped: Object.keys(faceMappings).length
            }).catch(e => {
              console.error('Firestore Error: ', JSON.stringify({
                error: e.message,
                operationType: 'create',
                path: 'users/' + uid + '/swapHistory',
                authInfo: { userId: uid }
              }));
            });
          }"""

code = code.replace(success_block, success_replacement)

with open("components/FaceMappingStudio.tsx", "w") as f:
    f.write(code)
print("patched FaceMappingStudio.tsx")
