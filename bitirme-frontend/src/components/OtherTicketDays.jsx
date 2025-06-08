import { useRef } from "react";
import { Col } from "antd";
import { FaChevronLeft, FaChevronRight } from "react-icons/fa";
import dayjs from "dayjs";

const OtherTicketDays = ({ flightData7DaysMinPrice, handleOtherTicketSearch }) => {
  const dates = flightData7DaysMinPrice.map((date) => {
    const formattedDate = dayjs(date.departureDate);
    return {
      day: formattedDate.format("DD"), // Gün
      weekday: formattedDate.format("dddd"), // Haftanın günü
      month: formattedDate.format("MMMM"), // Ay
      price: `$ ${date.priceRounded.units}`, // Fiyat (Yuvarlanmış)
      fullDate: date.departureDate, // Tam Tarih
    };
  });
  const scrollRef = useRef(null);

  const handleScroll = (direction) => {
    if (scrollRef.current) {
      const scrollAmount = 300; // Kayma mesafesi (piksel)
      scrollRef.current.scrollBy({
        left: direction === "left" ? -scrollAmount : scrollAmount,
        behavior: "smooth", // Yumuşak kayma
      });
    }
  };

  return (
    <div className="flex items-center justify-center px-2 sm:px-5 md:px-10 lg:px-20 xl:px-32 mt-10">
      <button
        className="bg-white hover:bg-gray-100 hover:bg-opacity-50 flex items-center justify-center border border-gray-200 transition-colors duration-300 font-bold text-2xl mr-3 py-2 px-5 rounded-md"
        onClick={() => handleScroll("left")}
      >
        <FaChevronLeft className="text-gray-500" />
      </button>

      <div
        ref={scrollRef}
        className="relative w-full mx-5 py-2 flex space-x-4 overflow-x-auto"
      >
        {dates.map((date, index) => (
          <Col
            key={index}
            xs={24}
            sm={12}
            md={8}
            lg={6}
            xl={4}
            className="flex justify-center"
          >
            <div onClick={() => handleOtherTicketSearch(date.fullDate)} className="bg-white cursor-pointer shadow-xl border rounded-lg w-full h-full flex flex-col p-5 items-center relative">
              <div className="flex justify-around items-center mb-1">
                <div className="text-4xl font-semibold">{date.day}</div>
                <div className="flex flex-col ml-3">
                  <span className="text-lg font-medium">{date.weekday}</span>
                  <span className="text-sm text-gray-600">{date.month}</span>
                </div>
              </div>
              <div className="text-center font-semibold text-xl mt-1 text-green-600">
                {date.price}
              </div>
              <span className="absolute -top-[5%] left-[80%] transform -translate-x-1/2 bg-white border-2 shadow-sm w-4 h-4 rounded-full"></span>
              <span className="absolute -top-[5%] left-[20%] transform -translate-x-1/2 bg-white border-2 shadow-sm w-4 h-4 rounded-full"></span>
            </div>
          </Col>
        ))}
      </div>

      <button
        className="bg-white hover:bg-gray-100 hover:bg-opacity-50 flex items-center justify-center border border-gray-200 transition-colors duration-300 font-bold text-2xl mr-3 py-2 px-5 rounded-md"
        onClick={() => handleScroll("right")}
      >
        <FaChevronRight className="text-gray-500" />
      </button>
    </div>
  );
};

export default OtherTicketDays;
