import { useForm, Controller } from "react-hook-form";
import { ISSUE_CATEGORIES, ISSUE_PRIORITIES } from "../utils/constants";
import ImageUploader from "./ImageUploader";
import LocationPicker from "./LocationPicker";

export default function IssueForm({ onSubmit }) {
  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting },
  } = useForm({
    defaultValues: {
      category: ISSUE_CATEGORIES[0],
      priority: ISSUE_PRIORITIES[2],
      description: "",
      image: null,
      location: { latitude: "", longitude: "" },
    },
  });

  function submitHandler(data) {
    onSubmit ? onSubmit(data) : console.log("Issue submitted", data);
  }

  return (
    <form
      onSubmit={handleSubmit(submitHandler)}
      onReset={() => reset()}
      className="flex flex-col gap-6 rounded-2xl border border-slate-200/60 bg-white/70 p-6 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50"
    >
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label className="flex flex-col gap-1 text-sm">
          Category
          <select
            {...register("category", { required: true })}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-800 dark:bg-slate-900"
          >
            {ISSUE_CATEGORIES.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1 text-sm">
          Priority
          <select
            {...register("priority", { required: true })}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-800 dark:bg-slate-900"
          >
            {ISSUE_PRIORITIES.map((priority) => (
              <option key={priority} value={priority}>
                {priority}
              </option>
            ))}
          </select>
        </label>
      </div>

      <label className="flex flex-col gap-1 text-sm">
        Description
        <textarea
          rows={4}
          placeholder="Describe the issue..."
          {...register("description", { required: "A description is required.", minLength: 10 })}
          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-800 dark:bg-slate-900"
        />
        {errors.description && (
          <span className="text-xs text-red-500" role="alert">
            {errors.description.message || "Please add a longer description."}
          </span>
        )}
      </label>

      <Controller
        name="location"
        control={control}
        render={({ field }) => <LocationPicker location={field.value} setLocation={field.onChange} />}
      />

      <Controller
        name="image"
        control={control}
        render={({ field }) => <ImageUploader image={field.value} setImage={field.onChange} />}
      />

      <div className="flex flex-wrap gap-4">
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-lg bg-amber-500 px-6 py-3 font-semibold text-white transition-colors hover:bg-amber-600 disabled:opacity-60"
        >
          {isSubmitting ? "Submitting..." : "Submit Report"}
        </button>
        <button
          type="reset"
          className="rounded-lg border border-slate-300 px-6 py-3 font-semibold text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
        >
          Reset
        </button>
      </div>
    </form>
  );
}