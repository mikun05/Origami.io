### PROJECT STRUCTURE ###
/origami
  /frontend                # React front-end
    /public                # Static files (HTML, CSS, etc.)
    /src                   # React components, hooks, etc.
      /components          # UI components
      /services            # Handles API requests to Python
    package.json           # Front-end dependencies

  /backend                 # Python back-end
    /app                   # Core Python logic
      /routes              # API routes/endpoints
      /models              # Data models (optional, if using DB)
      /services            # Additional services, incl. origami-related automation
      /scripts             # Scripts for automation or file handling with Origamizer
    /tests                 # Unit and integration tests for back-end
    requirements.txt       # Python dependencies

  /data                    # Input files (polyhedral surfaces)
  /results                 # Output files (creased patterns)
  /README.md               # Project overview and instructions


### NOTE TO SELF ###

Build/interact the existring origamizer software into a web base application.
This web based application takes in a non-polyhedral surface/3d object, ‘triangulates it’ so it is a polyhedral surface made up solely of triangle faces, run this through the origamizer to generate a valid water-tight crease pattern. 

The extensional aspect of this project involves having the web based software also fold this complex crease pattern. This will not be a simply collapsable fold, the order in which the folds are done matters hence why Dermaine and Tachi’s crease patterns from the Origamizer are ultimately folded by hand i.e., the stanford bunny. 

As well as attempting to develop an algorithm which decides the optimal order of folds for the crease pattern (having knowledge of both the crease pattern and the polyhedral surface it ought to look like), the web-based application will also allow users to ‘play’ the foldings in order, or in isolation in a way that might aid with folding it by hand themselves, or help understand how the software arrives at the final folded state.

**will need to request access to the codebase


1.	Delaunny triangulation of any 3d structure.
2.	Optimal way of cutting the 3d polyhedral surface into a flat mesh surface
    This is what gets passed into origamizer
3. retrieve crease pattern and compute optimal folding process (in terms of steps, what gets folded before what)
    ideallly this would be a playable step by step, 
    users can focus on a specific face and determine how to fold that