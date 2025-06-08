import { useState, useEffect } from "react";
import { FaTurkishLiraSign } from "react-icons/fa6";
import { Card, Spin } from "antd";
import { axiosPrivate } from "../api/axios";

const TravelCard = ({ city, country }) => {
  const [imageUrl, setImageUrl] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchCityImage = async () => {
      try {
        setIsLoading(true);
        const { data } = await axiosPrivate.get("/location/cityPhoto", {
          params: { cityName: city },
        });
        if (data.data && data.data[0]?.urls?.regular) {
          setImageUrl(data.data[Math.floor(Math.random() * 6)].urls.regular);
        }
      } catch (error) {
        console.error("Error fetching city image:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCityImage();
  }, [city]);

  return (
    <Card hoverable className="lg:w-full mb-2">
      <div className="flex gap-6 box-content">
        {isLoading ? (
          <div className="w-full flex ">
            <Spin />
          </div>
        ) : (
          <img
            src={imageUrl}
            alt={`${city}, ${country}`}
            className="h-[130px] w-[180px] rounded-l-lg"
          />
        )}
        <div className="flex flex-col gap-3 py-3">
          <div>
            <span className="font-bold text-[16px]">{city}</span>
            <p className="text-[12px] text-[#727272]">{country}</p>
          </div>

          <div>
            <p className="text-[12px] text-[#727272]">Round-trip from</p>
            <h2 className="flex items-baseline">
              <FaTurkishLiraSign size={10} />
              <span className="text-[20px] font-semibold ml-1">3.000</span>
            </h2>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default TravelCard;
