const MONTHS_NL = [
  "jan", "feb", "mrt", "apr", "mei", "jun",
  "jul", "aug", "sep", "okt", "nov", "dec",
];

export const todayISO = () => {
  const d = new Date();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${month}-${day}`;
};

export const formatCookedDate = (iso) => {
  if (!iso) return "";

  const [year, month, day] = iso.split("-").map(Number);
  const date = new Date(year, month - 1, day);

  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const diffDays = Math.round((today - date) / 86400000);

  if (diffDays === 0) return "Vandaag";
  if (diffDays === 1) return "Gisteren";

  return `${day} ${MONTHS_NL[month - 1]} ${year}`;
};
