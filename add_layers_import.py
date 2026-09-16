with open('app/page.tsx', 'r') as f:
    content = f.read()

import_statement = "import { UploadCloud, Image as ImageIcon, Video, Play, Loader2, CheckCircle2, Download, Scissors, History, X, Clock, ChevronLeft, ChevronRight, Layers } from 'lucide-react';"

content = content.replace(
    "import { UploadCloud, Image as ImageIcon, Video, Play, Loader2, CheckCircle2, Download, Scissors, History, X, Clock, ChevronLeft, ChevronRight } from 'lucide-react';",
    import_statement
)

with open('app/page.tsx', 'w') as f:
    f.write(content)
