
import React, { useState, useEffect } from 'react';
import { getArtworks } from '../services/api';
import { mockArtworks } from '../data/mockData';
import { useToast } from '../components/ui/use-toast';

interface Artwork {
  id: string;
  title: string;
  artist: string;
  description: string;
  price: number;
  imageUrl: string;
  medium: string;
  dimensions: string;
  year: number;
  status: string;
}

const ArtworksPage: React.FC = () => {
  const [artworks, setArtworks] = useState<Artwork[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const { toast } = useToast();

  useEffect(() => {
    const fetchArtworks = async () => {
      try {
        const response = await getArtworks();
        if (response && response.artworks) {
          setArtworks(response.artworks);
        } else {
          // Fallback to mock data if API response doesn't have expected structure
          console.log('Using mock artwork data as fallback');
          setArtworks(mockArtworks);
        }
      } catch (error) {
        console.error('Failed to fetch artworks:', error);
        // Use mock data on error
        setArtworks(mockArtworks);
        toast({
          title: "Error",
          description: "Failed to load artworks. Using sample data instead.",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchArtworks();
  }, [toast]);

  if (loading) {
    return (
      <div className="container mx-auto py-12 flex justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-12 px-4">
      <h1 className="text-4xl font-bold mb-8 text-center">Artworks Collection</h1>
      
      {artworks.length === 0 ? (
        <div className="text-center text-gray-500">
          <p>No artworks available at the moment.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {artworks.map((artwork) => (
            <div key={artwork.id} className="bg-white rounded-lg shadow-lg overflow-hidden">
              <div className="h-64 overflow-hidden">
                <img 
                  src={artwork.imageUrl || 'https://via.placeholder.com/400x300?text=Artwork+Image'} 
                  alt={artwork.title}
                  className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
                />
              </div>
              <div className="p-6">
                <h2 className="text-xl font-semibold mb-2">{artwork.title}</h2>
                <p className="text-gray-600 mb-1">by {artwork.artist}</p>
                <p className="text-gray-600 mb-1">{artwork.medium}, {artwork.year}</p>
                <p className="text-gray-600 mb-4">{artwork.dimensions}</p>
                <div className="flex justify-between items-center">
                  <span className="text-xl font-bold text-primary">KSh {artwork.price.toLocaleString()}</span>
                  <button className="bg-primary text-white px-4 py-2 rounded hover:bg-primary/90 transition">
                    View Details
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ArtworksPage;
