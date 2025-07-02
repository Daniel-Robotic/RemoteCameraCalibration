from calibration import ChessBoard, CircleGridBoard, ArucoBoard, CharucoBoard

grid_cells = (5, 7)
cell_size_mm = 40
dpi = 600
paper_size_mm = "A4"

chessboard = ChessBoard(
    grid_cells=grid_cells,
    cell_size_mm=cell_size_mm,
    dpi=dpi,
    paper_size_mm=paper_size_mm
)

circlegridboard_sym = CircleGridBoard(
    grid_cells=grid_cells,
    cell_size_mm=cell_size_mm,
    dpi=dpi,
    paper_size_mm=paper_size_mm,
    asymmetric=False
)

circlegridboard_asym = CircleGridBoard(
    grid_cells=grid_cells,
    cell_size_mm=cell_size_mm,
    dpi=dpi,
    paper_size_mm=paper_size_mm,
    asymmetric=True
)

arucoboard = ArucoBoard(
    grid_cells=grid_cells,
    cell_size_mm=cell_size_mm,
    marker_length_ratio=0.75,
    dpi=dpi,
    paper_size_mm=paper_size_mm,
    aruco_dict_name="5x5_250"
)

charucoboard = CharucoBoard(
    grid_cells=grid_cells,
    cell_size_mm=cell_size_mm,
    marker_length_mm=25,
    dpi=dpi,
    paper_size_mm=paper_size_mm,
    aruco_dict_name="4x4_50"
)

chessboard.generate_board(filename="./chessboard.pdf")
circlegridboard_sym.generate_board(filename="./circlegridboard_sym.png")
circlegridboard_asym.generate_board(filename="./circlegridboard_asym.jpg")
arucoboard.generate_board(filename="./arucoboard.pdf")
charucoboard.generate_board(filename="./charucoboard.pdf")