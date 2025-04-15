import React, { useState, useEffect } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { ArtworkData } from "@/services/api";
import { ImageUp } from "lucide-react";

const MAX_FILE_SIZE = 5000000; // 5MB
const ACCEPTED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"];

const artworkSchema = z.object({
  title: z.string().min(3, { message: "Title must be at least 3 characters" }),
  artist: z.string().min(3, { message: "Artist name must be at least 3 characters" }),
  description: z.string().min(10, { message: "Description must be at least 10 characters" }),
  price: z.coerce.number().min(0, { message: "Price must be a positive number" }),
  dimensions: z.string().optional(),
  medium: z.string().optional(),
  year: z.coerce.number().int().min(1000).max(new Date().getFullYear()).optional(),
  status: z.enum(["available", "sold"], { message: "Status must be available or sold" }),
});

type ArtworkFormValues = z.infer<typeof artworkSchema>;

interface ArtworkFormProps {
  initialData?: ArtworkData;
  onSubmit: (data: ArtworkData) => void;
  onCancel: () => void;
}

const ArtworkForm: React.FC<ArtworkFormProps> = ({
  initialData,
  onSubmit,
  onCancel,
}) => {
  const { toast } = useToast();
  
  const [imageUrl, setImageUrl] = useState<string>(initialData?.imageUrl || "");
  const [previewImage, setPreviewImage] = useState<string | null>(
    initialData?.imageUrl ? initialData.imageUrl : null
  );
  const [fileName, setFileName] = useState<string>("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [isImageLoaded, setIsImageLoaded] = useState<boolean>(!!initialData?.imageUrl);
  
  const defaultValues: ArtworkFormValues = initialData ? {
    title: initialData.title,
    artist: initialData.artist,
    description: initialData.description,
    price: initialData.price,
    dimensions: initialData.dimensions || "",
    medium: initialData.medium || "",
    year: initialData.year || new Date().getFullYear(),
    status: initialData.status as "available" | "sold",
  } : {
    title: "",
    artist: "",
    description: "",
    price: 0,
    dimensions: "",
    medium: "",
    year: new Date().getFullYear(),
    status: "available" as const,
  };

  const form = useForm<ArtworkFormValues>({
    resolver: zodResolver(artworkSchema),
    defaultValues,
  });

  useEffect(() => {
    if (initialData?.imageUrl) {
      const img = new Image();
      img.onload = () => {
        setIsImageLoaded(true);
        console.log("Image loaded successfully:", initialData.imageUrl);
      };
      img.onerror = () => {
        console.error("Failed to load image:", initialData.imageUrl);
        setIsImageLoaded(false);
        setPreviewImage("/placeholder.svg");
      };
      img.src = initialData.imageUrl;
    }
  }, [initialData?.imageUrl]);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    
    if (!files || files.length === 0) return;
    
    const file = files[0];
    setImageFile(file);
    
    if (file.size > MAX_FILE_SIZE) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Image size should be less than 5MB",
      });
      return;
    }
    
    if (!ACCEPTED_IMAGE_TYPES.includes(file.type)) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Image format should be JPG, PNG or WebP",
      });
      return;
    }
    
    const now = new Date();
    const dateTime = now.getFullYear() +
                    String(now.getMonth() + 1).padStart(2, '0') +
                    String(now.getDate()).padStart(2, '0') +
                    String(now.getHours()).padStart(2, '0') +
                    String(now.getMinutes()).padStart(2, '0') +
                    String(now.getSeconds()).padStart(2, '0');
    
    const generatedFileName = `${dateTime}_${file.name.replace(/\s+/g, '-')}`;
    setFileName(generatedFileName);
    
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      setPreviewImage(result);
      setImageUrl(result);
      setIsImageLoaded(true);
    };
    reader.readAsDataURL(file);
    
    console.log("Image prepared for upload with filename:", generatedFileName);
  };

  const handleSubmit = async (values: ArtworkFormValues) => {
    try {
      if (!imageUrl && !previewImage) {
        toast({
          variant: "destructive",
          title: "Image Required",
          description: "Please upload an image for the artwork",
        });
        return;
      }
      
      let submissionImageUrl = imageUrl;
      
      if (initialData?.imageUrl && !imageFile && 
          (initialData.imageUrl.startsWith('/static/') || 
           initialData.imageUrl.startsWith('http'))) {
        submissionImageUrl = initialData.imageUrl;
        console.log("Using existing server image path:", submissionImageUrl);
      }
      
      console.log("Submitting artwork with image URL type:", typeof submissionImageUrl);
      
      const submissionData = {
        ...values,
        imageUrl: submissionImageUrl,
        price: values.price
      } as ArtworkData;
      
      onSubmit(submissionData);
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to submit artwork. Please try again.",
      });
      console.error("Submit error:", error);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Title</FormLabel>
              <FormControl>
                <Input placeholder="Artwork title" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <FormField
          control={form.control}
          name="artist"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Artist</FormLabel>
              <FormControl>
                <Input placeholder="Artist name" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description</FormLabel>
              <FormControl>
                <Textarea placeholder="Artwork description" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <div className="space-y-2">
          <FormLabel>Artwork Image</FormLabel>
          <div className="flex flex-col items-center p-4 border-2 border-dashed border-gray-300 rounded-lg">
            {previewImage && (
              <div className="mb-4 w-full max-w-xs">
                <img 
                  src={previewImage} 
                  alt="Artwork preview" 
                  className="w-full h-auto rounded-lg"
                  onError={(e) => {
                    console.error("Image failed to load:", previewImage);
                    (e.target as HTMLImageElement).src = '/placeholder.svg';
                  }}
                />
              </div>
            )}
            
            <label className="w-full flex flex-col items-center px-4 py-6 bg-white rounded-lg cursor-pointer hover:bg-gray-50">
              <ImageUp className="w-8 h-8 text-gray-500" />
              <span className="mt-2 text-base text-gray-500">
                {previewImage ? "Change image" : "Upload image"}
              </span>
              <input type="file" className="hidden" onChange={handleImageChange} accept="image/*" />
            </label>
            
            {previewImage && (
              <p className="text-sm text-gray-500 mt-2">
                {isImageLoaded ? 
                  "Click above to change the image" : 
                  "Current image may not be displaying correctly. Please upload a new one."}
              </p>
            )}
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="dimensions"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Dimensions</FormLabel>
                <FormControl>
                  <Input placeholder="e.g. 24 x 36 inches" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          
          <FormField
            control={form.control}
            name="medium"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Medium</FormLabel>
                <FormControl>
                  <Input placeholder="e.g. Oil on canvas" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="price"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Price (KSh)</FormLabel>
                <FormControl>
                  <Input type="number" min="0" step="0.01" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          
          <FormField
            control={form.control}
            name="year"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Year</FormLabel>
                <FormControl>
                  <Input type="number" min="1000" max={new Date().getFullYear()} {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
        
        <FormField
          control={form.control}
          name="status"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Status</FormLabel>
              <FormControl>
                <select 
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-base ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm"
                  {...field}
                >
                  <option value="available">Available</option>
                  <option value="sold">Sold</option>
                </select>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <div className="flex justify-end gap-2 pt-4">
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit">
            {initialData ? "Update Artwork" : "Create Artwork"}
          </Button>
        </div>
      </form>
    </Form>
  );
};

export default ArtworkForm;
