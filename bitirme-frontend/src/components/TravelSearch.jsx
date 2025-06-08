import { useCallback, useEffect, useState } from "react";
import { IoSwapHorizontal } from "react-icons/io5";
import TravelSearchInput from "./TravelSearchInput";
import TravelDateInput from "./TravelDateInput";
import TravelPassengersAndClassType from "./TravelPassengersAndClassType";
import { axiosPrivate } from "../api/axios";
import { Spin } from "antd";
import dayjs from "dayjs";
import { useNavigate } from 'react-router-dom';

const TravelSearch = ({ selectType }) => {
  const router = useNavigate();
  const [fromValue, setFromValue] = useState("");
  const [toValue, setToValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [countries, setCountries] = useState([]);
  const [flightInfo, setFlightInfo] = useState({
    from: "",
    to: "",
    fromCode: "",
    toCode: "",
    dates: {
      departDate: "",
      returnDate: "",
    },
    passengers: {
      adult: 1,
      children: 0,
      infants: 0,
    },
    classType: "economy",
  });

  const updateFlightInfo = useCallback((key, value) => {
    setFlightInfo((prevState) => ({
      ...prevState,
      [key]:
        typeof value === "object" ? { ...prevState[key], ...value } : value,
    }));
  }, []);

  useEffect(() => {
    const fetchCountries = async () => {
      try {
        setLoading(true);
        const { data } = await axiosPrivate.get("/location/countries");
        setCountries(data.data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching countries:", error);
        setLoading(false);
      }
    };

    fetchCountries();
  }, []);

  const handleSwap = () => {
    setFromValue(toValue);
    setToValue(fromValue);
    updateFlightInfo("fromCode", flightInfo.toCode);
    updateFlightInfo("toCode", flightInfo.fromCode);
  };

  const handleSearch = async () => {
    updateFlightInfo("from", fromValue);
    updateFlightInfo("to", toValue);
    try {
      setLoading(true);
      const formattedDate = dayjs(flightInfo.dates.departDate).format("YYYY-MM-DD");
      const oneWay = await axiosPrivate.get("/flight/oneWay", {
        params: {
          from: flightInfo.fromCode,
          to: flightInfo.toCode,
          date: formattedDate,
          adults: flightInfo.passengers.adult,
          children: flightInfo.passengers.children,
          infants: flightInfo.passengers.infants,
          cabinClass: flightInfo.classType,
        },
      });
      const oneWay7DaysMinPrice = await axiosPrivate.get("/flight/oneWay7DaysMinPrice", {
        params: {
          fromId: flightInfo.fromCode.toLocaleUpperCase(),
          toId: flightInfo.toCode.toLocaleUpperCase(),
          departDate: formattedDate,
          cabinClass: flightInfo.classType.toLocaleUpperCase(),
        },
      });

      setLoading(false);
      router(`/ticket/${oneWay.data.data.data.flightsSessionId}`, {
        state: {
          fromValue,
          toValue,
          flightInfo,
          flightData: oneWay.data.data.data.itineraries,
          flightData7DaysMinPrice: oneWay7DaysMinPrice.data.data.data,
        },
      });
    } catch (error) {
      console.error("Error fetching flights:", error);
      setLoading(false);
    }
  };
  // Memoize the setCode callbacks
  const handleFromCode = useCallback(
    (code) => {
      updateFlightInfo("fromCode", code);
    },
    [updateFlightInfo]
  );

  const handleToCode = useCallback(
    (code) => {
      updateFlightInfo("toCode", code);
    },
    [updateFlightInfo]
  );

  return loading ? (
    <Spin />
  ) : (
    <div>
      <div className="my-4 flex flex-col sm:flex-col md:flex-col lg:flex-row xl:flex-row justify-between gap-3 items-center relative">
        <div className="flex w-full items-center">
          <TravelSearchInput
            title={"From"}
            value={fromValue}
            setValue={setFromValue}
            setCode={handleFromCode}
            leftMargin={12}
            countries={countries}
          />
          <div className="relative cursor-pointer group" onClick={handleSwap}>
            <div className="absolute z-10 bg-white -bottom-5 -left-3 p-3 border border-gray-300 group-hover:border-gray-400 rounded-full">
              <IoSwapHorizontal className="w-5 h-5 text-gray-400 group-hover:text-gray-500" />
            </div>
          </div>
          <div className="pl-5 w-full">
            <TravelSearchInput
              title={"To"}
              value={toValue}
              setValue={setToValue}
              setCode={handleToCode}
              leftMargin={20}
              countries={countries}
            />
          </div>
        </div>
        <TravelDateInput
          title={"Depart"}
          date={flightInfo.dates.departDate}
          setDate={(date) => updateFlightInfo("dates", { departDate: date })}
        />
        {selectType === 2 && (
          <TravelDateInput
            title={"Return"}
            date={flightInfo.dates.returnDate}
            setDate={(date) => updateFlightInfo("dates", { returnDate: date })}
          />
        )}
      </div>
      <div className="flex justify-end items-center select-none">
        <TravelPassengersAndClassType
          classType={flightInfo.classType}
          setClassType={(value) => updateFlightInfo("classType", value)}
          passengers={flightInfo.passengers}
          setPassengers={(passengerInfo) =>
            updateFlightInfo("passengers", passengerInfo)
          }
        />
        <div
          onClick={handleSearch}
          className="bg-green-600 cursor-pointer hover:bg-green-700 py-2 px-4 ml-3 rounded-full text-white font-semibold"
        >
          <button>Search</button>
        </div>
      </div>
    </div>
  );
};

export default TravelSearch;
