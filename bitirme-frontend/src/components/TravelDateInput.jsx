import { Input, Button } from "antd";
import { Calendar, theme } from "antd";
import { useEffect, useState } from "react";
import dayjs from 'dayjs';

const TravelDateInput = ({ title, date, setDate }) => {
  const [isDateActive, setIsDateActive] = useState(false);
  const [tempDate, setTempDate] = useState(null);
  const { token } = theme.useToken();

  // Parse the date string to dayjs object
  const selectedDate = date ? dayjs(date, 'ddd, DD MMM YYYY') : dayjs();

  const wrapperStyle = {
    position: "absolute",
    top: "100%",
    left: 0,
    zIndex: 10,
    backgroundColor: "white",
    border: `1px solid ${token.colorBorderSecondary}`,
    borderRadius: token.borderRadiusLG,
    width: "100%",
  };

  const handleDateChange = (value) => {
    setTempDate(value);
  };

  const handleConfirmDate = () => {
    if (tempDate) {
      setDate(tempDate.format("ddd, DD MMM YYYY"));
    }
    setIsDateActive(false);
  };

  const handleInputClick = () => {
    setIsDateActive(!isDateActive);
    if (!isDateActive) {
      setTempDate(selectedDate);
    }
  };

  const handleClickOutside = (event) => {
    if (
      !event.target.closest(".calendar-container") &&
      !event.target.closest(".calendar-input")
    ) {
      setIsDateActive(false);
    }
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <div className="w-[50%] flex items-center pb-2 mt-3 lg:mt-0 xl:mt-0 relative">
      <div
        style={{ position: "relative", width: "100%" }}
        className="cursor-pointer calendar-input"
        onClick={handleInputClick}
      >
        <div
          style={{
            position: "absolute",
            zIndex: "1",
            top: "4px",
            left: "12px",
            fontSize: "12px",
            color: "#999",
          }}
        >
          {title}
        </div>
        <Input
          placeholder="Select Date"
          value={date}
          className="cursor-pointer"
          readOnly
          style={{
            paddingTop: "18px",
            paddingLeft: "12px",
            paddingBottom: "10px",
            fontSize: "20px",
          }}
        />
      </div>
      {isDateActive && (
        <div style={wrapperStyle} className="calendar-container">
          <Calendar
            fullscreen={false}
            onChange={handleDateChange}
            value={tempDate || selectedDate}
            defaultValue={selectedDate}
          />
          <div style={{ display: 'flex', justifyContent: 'flex-end', paddingRight: 6, borderTop: `1px solid ${token.colorBorderSecondary}` }}>
            <Button size="small" type="link" onClick={handleConfirmDate}>
              OK
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default TravelDateInput;
