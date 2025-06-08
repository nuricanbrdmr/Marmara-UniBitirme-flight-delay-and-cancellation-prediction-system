import mongoose from "mongoose";
import bcrypt from "bcrypt";

const emailRegex = /^\S+@\S+\.\S+$/;
const userSchema = new mongoose.Schema(
  {
    email: {
      type: String,
      required: true,
      trim: true,
      unique: true,
      match: [emailRegex, "Invalid email address"],
    },
    password: {
      type: String,
      required: true,
      trim: true,
      maxLength: 16,
      minLength: 4,
    },
    verifytoken: {
      type: String,
      require: false,
    },
    admin: {
      type: Boolean,
      default: false,
    },
  },

  { timestamps: true }
);

userSchema.pre("save", async function (next) {
  try {
    const salt = await bcrypt.genSalt(10);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

const User = mongoose.model("User", userSchema);
export default User;
