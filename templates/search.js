window.onload = async function load() {
  get_animes();
};
async function get_animes() {
  const queryParams = new URLSearchParams(window.location.search);
const query = queryParams.get("query");

if (query) {
  // Make a GET request to the API endpoint with the user's search query
  fetch(`http://127.0.0.1:5001/anime/search?query=${encodeURIComponent(query)}`, {
    method: "GET",
    credentials: "include",
  });
  const data = await res.json();

  display_animes(data.animes);
}

function display_animes(animes) {
  animes.forEach(create_anime) //for each story we add the dynamic text below
}

function create_anime(anime) {
  const stories = document.getElementById('anime-titles')
  const storyWrapper = document.createElement('div') // what ever in storyRapper, is assigned to html but as a dynamic "text" so changes.
  let point = 'points'
  if (story.score == 1) {
    point = 'point'
  }
  storyWrapper.innerHTML = `
	<p>
		<a class="title">${anime.title} </a>

	</p>`


}
    // .then((response) => response.json())
    // .then((data) => {
//       console.log(response);
//       const animeTitles = data.animes;
//       const animeList = document.getElementById("anime-titles");

//       // Clear the previous anime titles from the list
//       animeList.innerHTML = "";

//       // Populate the HTML list with anime titles
//       animeTitles.forEach((title) => {
//         const listItem = document.createElement("li");
//         listItem.textContent = title;
//         listItem.addEventListener("click", () => {
//           // Handle anime selection here
//           handleAnimeSelection(title);
//         });
//         animeList.appendChild(listItem);
//       });
//     })
//     .catch((error) => {
//       console.error("Error:", error);
//     });
// } else {
//   console.log("Anime search query not found in the URL.");
// }

// // Function to handle anime selection
// function handleAnimeSelection(title) {
//   // Do something with the selected anime title, such as making another API request to get detailed information
//   console.log("Selected anime:", title);
// }
