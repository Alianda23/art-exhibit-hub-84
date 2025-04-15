
import React, { useState, useEffect } from 'react';
import { getExhibitions } from '../services/api';
import { mockExhibitions } from '../data/mockData';
import { useToast } from '../components/ui/use-toast';
import { CalendarIcon, MapPinIcon, TicketIcon } from 'lucide-react';

interface Exhibition {
  id: string;
  title: string;
  description: string;
  location: string;
  startDate: string;
  endDate: string;
  ticketPrice: number;
  imageUrl: string;
  totalSlots: number;
  availableSlots: number;
  status: string;
}

const ExhibitionsPage: React.FC = () => {
  const [exhibitions, setExhibitions] = useState<Exhibition[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const { toast } = useToast();

  useEffect(() => {
    const fetchExhibitions = async () => {
      try {
        const response = await getExhibitions();
        if (response && response.exhibitions) {
          setExhibitions(response.exhibitions);
        } else {
          // Fallback to mock data if API response doesn't have expected structure
          console.log('Using mock exhibition data as fallback');
          setExhibitions(mockExhibitions);
        }
      } catch (error) {
        console.error('Failed to fetch exhibitions:', error);
        // Use mock data on error
        setExhibitions(mockExhibitions);
        toast({
          title: "Error",
          description: "Failed to load exhibitions. Using sample data instead.",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchExhibitions();
  }, [toast]);

  if (loading) {
    return (
      <div className="container mx-auto py-12 flex justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Format date for display
  const formatDate = (dateString: string) => {
    const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
  };

  return (
    <div className="container mx-auto py-12 px-4">
      <h1 className="text-4xl font-bold mb-8 text-center">Upcoming Exhibitions</h1>
      
      {exhibitions.length === 0 ? (
        <div className="text-center text-gray-500">
          <p>No exhibitions scheduled at the moment.</p>
        </div>
      ) : (
        <div className="space-y-8">
          {exhibitions.map((exhibition) => (
            <div key={exhibition.id} className="bg-white rounded-lg shadow-lg overflow-hidden sm:flex">
              <div className="sm:w-1/3 h-64 sm:h-auto">
                <img 
                  src={exhibition.imageUrl || 'https://via.placeholder.com/400x300?text=Exhibition+Image'} 
                  alt={exhibition.title}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="p-6 sm:w-2/3">
                <h2 className="text-2xl font-semibold mb-2">{exhibition.title}</h2>
                <p className="text-gray-700 mb-4">{exhibition.description}</p>
                
                <div className="space-y-2 text-gray-600 mb-6">
                  <div className="flex items-center">
                    <CalendarIcon className="mr-2 h-5 w-5" />
                    <span>{formatDate(exhibition.startDate)} - {formatDate(exhibition.endDate)}</span>
                  </div>
                  <div className="flex items-center">
                    <MapPinIcon className="mr-2 h-5 w-5" />
                    <span>{exhibition.location}</span>
                  </div>
                  <div className="flex items-center">
                    <TicketIcon className="mr-2 h-5 w-5" />
                    <span>KSh {exhibition.ticketPrice.toLocaleString()} per ticket</span>
                  </div>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className={exhibition.availableSlots > 0 ? "text-green-500 font-medium" : "text-red-500 font-medium"}>
                    {exhibition.availableSlots > 0 
                      ? `${exhibition.availableSlots} tickets available` 
                      : 'Sold Out'}
                  </span>
                  <button 
                    className={`px-4 py-2 rounded transition ${
                      exhibition.availableSlots > 0 
                        ? 'bg-primary text-white hover:bg-primary/90' 
                        : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    }`}
                    disabled={exhibition.availableSlots === 0}
                  >
                    {exhibition.availableSlots > 0 ? 'Book Tickets' : 'Sold Out'}
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

export default ExhibitionsPage;
