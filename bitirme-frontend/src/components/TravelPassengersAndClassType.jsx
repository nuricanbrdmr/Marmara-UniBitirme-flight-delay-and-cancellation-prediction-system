import { Dropdown, Space } from "antd";
import { IoIosArrowDown } from "react-icons/io";
import { LuBaby } from "react-icons/lu";
import { FaChild } from "react-icons/fa";
import { SlUser } from "react-icons/sl";
import { useState } from "react";

const TravelPassengersAndClassType = ({
  classType,
  setClassType,
  passengers,
  setPassengers,
}) => {
  const [isPassengersActive, setIsPassengersActive] = useState(false);

  const passengerTypes = [
    {
      title: "Adults",
      subtitle: "<12 Years",
      icon: <SlUser className="w-6 h-6" />,
      key: "adult",
    },
    {
      title: "Children",
      subtitle: "2-12 years",
      icon: <FaChild className="w-6 h-6" />,
      key: "children",
    },
    {
      title: "Infants",
      subtitle: ">2 years",
      icon: <LuBaby className="w-6 h-6" />,
      key: "infants",
    },
  ];

  const onClick = ({ key }) => {
    setClassType(key);
  };

  const items = [
    {
      label: "Economy",
      key: "economy",
    },
    {
      label: "Premium Economy",
      key: "premium_economy",
    },
    {
      label: "Business Class",
      key: "business",
    },
    {
      label: "First Class",
      key: "first",
    },
  ];

  const handleCountChange = (type, delta) => {
    const newCount = Math.max(0, passengers[type] + delta);
    const updatedPassengers = {
      ...passengers,
      [type]: newCount,
    };
    setPassengers(updatedPassengers);
  };

  const totalPassengers = passengers
    ? Object.values(passengers).reduce((acc, count) => acc + count, 0)
    : 0;

  const wrapperStyle = {
    position: "absolute",
    top: "96%",
    left: "60%",
    zIndex: 10,
    backgroundColor: "white",
    width: "30%",
  };

  return (
    <>
      <div className="flex justify-end items-center select-none">
        <div
          onClick={() => setIsPassengersActive(!isPassengersActive)}
          className="flex items-center cursor-pointer mr-2 gap-2 text-gray-600 hover:text-black hover:bg-gray-200 hover:bg-opacity-60 p-1 rounded-lg"
        >
          {`${totalPassengers} Passengers`}{" "}
          <IoIosArrowDown className="w-5 h-5 opacity-70" />
        </div>
        <Dropdown
          menu={{
            items,
            onClick,
          }}
          value={classType}
          className="hover:bg-gray-200 bg-transparent transition-all p-1 rounded-lg text-gray-600 hover:text-black"
        >
          <a onClick={(e) => e.preventDefault()}>
            <Space>
              {items.find((item) => item.key === classType)?.label || "Economy"}
              <IoIosArrowDown className="w-5 h-5 opacity-70" />
            </Space>
          </a>
        </Dropdown>
      </div>
      {isPassengersActive && (
        <div
          style={wrapperStyle}
          className="shadow-xl flex flex-col gap-5 rounded-lg min-h-[200px] p-3 border"
        >
          {passengerTypes.map((passenger) => (
            <div
              key={passenger.key}
              className="flex justify-between items-center gap-5"
            >
              <div className="flex items-center gap-5">
                {passenger.icon}
                <div className="flex flex-col">
                  <span className="text-[16px]">{passenger.title}</span>
                  <span className="text-[12px]">{passenger.subtitle}</span>
                </div>
              </div>
              <div className="flex justify-center items-center gap-3">
                <button
                  type="button"
                  onClick={() => handleCountChange(passenger.key, -1)}
                  className="bg-green-600 hover:bg-green-500 w-5 text-white shadow-lg px-1 rounded-[4px] font-bold text-xl"
                >
                  -
                </button>
                <span className="text-xl">
                  {passengers?.[passenger.key] || 0}
                </span>
                <button
                  type="button"
                  onClick={() => handleCountChange(passenger.key, 1)}
                  className="bg-green-600 hover:bg-green-500 w-5 text-white shadow-lg px-1 rounded-[4px] font-bold text-lg"
                >
                  +
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
};

export default TravelPassengersAndClassType;
