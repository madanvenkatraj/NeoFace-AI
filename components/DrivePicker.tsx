'use client';
import { useState, useEffect } from 'react';
import { Cloud, Loader2 } from 'lucide-react';
import { getAccessToken, googleSignIn } from '../lib/firebase'; // Adjust if auth is elsewhere

interface DrivePickerProps {
  onFilePicked: (file: { id: string; name: string; url: string; mimeType: string }) => void;
  className?: string;
  label?: string;
}

export default function DrivePicker({ onFilePicked, className = '', label = 'Select from Drive' }: DrivePickerProps) {
  const [isPickerLoaded, setIsPickerLoaded] = useState(false);
  const [isPicking, setIsPicking] = useState(false);

  useEffect(() => {
    // Load the Google API script for the picker
    const loadScript = () => {
      const script = document.createElement('script');
      script.src = 'https://apis.google.com/js/api.js';
      script.onload = () => {
        (window as any).gapi.load('picker', () => {
          setIsPickerLoaded(true);
        });
      };
      document.body.appendChild(script);
    };

    if (!(window as any).gapi) {
      loadScript();
    } else if (!(window as any).google?.picker) {
      (window as any).gapi.load('picker', () => {
        setIsPickerLoaded(true);
      });
    } else {
      setTimeout(() => setIsPickerLoaded(true), 0);
    }
  }, []);

  const openPicker = async () => {
    if (!isPickerLoaded) return;
    
    setIsPicking(true);
    try {
      let token = await getAccessToken();
      if (!token) {
        // Attempt to sign in to get the token
        const result = await googleSignIn();
        if (result?.accessToken) {
          token = result.accessToken;
        } else {
          throw new Error('Failed to get access token');
        }
      }

      const pickerOrigin = window.location.ancestorOrigins && window.location.ancestorOrigins.length > 0 
        ? window.location.ancestorOrigins[window.location.ancestorOrigins.length - 1] 
        : window.location.origin;

      const view = new (window as any).google.picker.DocsView((window as any).google.picker.ViewId.DOCS);
      view.setMimeTypes('image/png,image/jpeg,image/jpg,video/mp4,video/quicktime');

      const picker = new (window as any).google.picker.PickerBuilder()
        .addView(view)
        .setOAuthToken(token)
        .setCallback((data: any) => {
          if (data.action === (window as any).google.picker.Action.PICKED) {
            const file = data.docs[0];
            onFilePicked({
              id: file.id,
              name: file.name,
              url: file.url,
              mimeType: file.mimeType
            });
          }
          if (data.action === (window as any).google.picker.Action.PICKED || data.action === (window as any).google.picker.Action.CANCEL) {
            setIsPicking(false);
          }
        })
        .setOrigin(pickerOrigin)
        .build();
        
      picker.setVisible(true);
    } catch (err) {
      console.error('Error opening picker:', err);
      setIsPicking(false);
    }
  };

  return (
    <button 
      onClick={openPicker}
      disabled={!isPickerLoaded || isPicking}
      className={`flex items-center gap-2 justify-center transition-all ${className}`}
    >
      {isPicking ? <Loader2 className="animate-spin" size={18} /> : <Cloud size={18} />}
      <span>{label}</span>
    </button>
  );
}
