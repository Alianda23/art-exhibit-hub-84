
// Mock data for when the API is unavailable

export const mockArtworks = [
  {
    id: '1',
    title: 'Sunset Over Nairobi',
    artist: 'James Mwangi',
    description: 'A stunning depiction of the Nairobi skyline at sunset, showcasing the vibrant colors and energy of Kenya\'s capital city.',
    price: 45000,
    imageUrl: 'https://images.unsplash.com/photo-1575550959106-5a7defe28b56?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    dimensions: '70cm x 90cm',
    medium: 'Oil on canvas',
    year: 2023,
    status: 'available'
  },
  {
    id: '2',
    title: 'Maasai Warriors',
    artist: 'Nancy Otieno',
    description: 'An expressive portrayal of Maasai warriors in traditional attire, celebrating their rich cultural heritage and resilience.',
    price: 38000,
    imageUrl: 'https://images.unsplash.com/photo-1523805009345-7448845a9e53?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    dimensions: '60cm x 80cm',
    medium: 'Acrylic on canvas',
    year: 2022,
    status: 'available'
  },
  {
    id: '3',
    title: 'Wildlife of Amboseli',
    artist: 'Peter Kamau',
    description: 'A detailed painting of elephants against the backdrop of Mount Kilimanjaro, captured in the golden light of the African savanna.',
    price: 52000,
    imageUrl: 'https://images.unsplash.com/photo-1521651201574-7f69e7f7e9ff?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    dimensions: '80cm x 100cm',
    medium: 'Oil on canvas',
    year: 2023,
    status: 'available'
  },
  {
    id: '4',
    title: 'Nairobi By Night',
    artist: 'Sophia Wambui',
    description: 'A modern interpretation of Nairobi\'s bustling nightlife, with vibrant colors representing the energy and spirit of the city after dark.',
    price: 35000,
    imageUrl: 'https://images.unsplash.com/photo-1596005554384-d293674c91d7?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    dimensions: '60cm x 75cm',
    medium: 'Mixed media',
    year: 2023,
    status: 'available'
  }
];

export const mockExhibitions = [
  {
    id: '1',
    title: 'Contemporary African Visions',
    description: 'Showcasing emerging Kenyan artists who are reshaping the contemporary art scene with bold expressions of identity and social commentary.',
    location: 'National Museum of Kenya, Nairobi',
    startDate: '2025-05-15',
    endDate: '2025-06-15',
    ticketPrice: 1200,
    imageUrl: 'https://images.unsplash.com/photo-1594122230689-45899d9e6f69?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    totalSlots: 500,
    availableSlots: 350,
    status: 'upcoming'
  },
  {
    id: '2',
    title: 'Traditions & Transitions',
    description: 'An exploration of how traditional Kenyan art forms are evolving in the 21st century, bridging ancestral techniques with modern perspectives.',
    location: 'Karen Village Art Center, Karen',
    startDate: '2025-06-10',
    endDate: '2025-07-10',
    ticketPrice: 1500,
    imageUrl: 'https://images.unsplash.com/photo-1547891654-e66ed7ebb968?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    totalSlots: 300,
    availableSlots: 220,
    status: 'upcoming'
  },
  {
    id: '3',
    title: 'Colors of Kenya',
    description: 'A vibrant celebration of Kenya\'s landscapes, wildlife, and cultural diversity through the eyes of prominent local artists.',
    location: 'Nairobi Gallery, CBD',
    startDate: '2025-07-20',
    endDate: '2025-08-20',
    ticketPrice: 1000,
    imageUrl: 'https://images.unsplash.com/photo-1582555172866-f73bb12a2ab3?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    totalSlots: 400,
    availableSlots: 400,
    status: 'upcoming'
  }
];
