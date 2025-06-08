import { useEffect, useState } from "react";
import Hero from "./Hero";
import Travel from "./Travel";
import TravelCard from "./TravelCard";
import { TravelType } from "../constant/TravelType";

const Home = () => {
  const [selectType, setSelectType] = useState(1);
  const [selectedCities, setSelectedCities] = useState([]);


  useEffect(() => {
    const cities =
      TravelType.find((type) => type.id === selectType)?.cities || [];
    setSelectedCities(cities);
  }, [selectType]);

  return (
    <div>
      <Hero />
      <div className="relative w-full">
        <div className="absolute w-full bottom-10 left-1/2 transform -translate-x-1/2 flex items-center justify-center z-10">
          <Travel />
        </div>
      </div>

      <div className="w-full flex justify-center">
        <div className="flex flex-col gap-5 py-10 w-[60%]">
          <h1 className="font-semibold text-2xl">Trip Ideas from Turkey</h1>
          <div className="flex items-center gap-3 flex-wrap">
            {TravelType.map((type) => (
              <div
                key={type.id}
                onClick={() => setSelectType(type.id)}
                className={`cursor-pointer text-opacity-80 py-2 px-4 rounded-full font-medium ${selectType === type.id
                    ? "bg-green-100 text-green-800"
                    : "bg-gray-200 bg-opacity-60 text-gray-900"
                  }`}
              >
                {type.title}
              </div>
            ))}
          </div>
          <div className="grid gap-2 grid-cols-1 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {selectedCities.map((cityData, index) => (
              <TravelCard
                key={index}
                city={cityData.city}
                country={cityData.country}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
