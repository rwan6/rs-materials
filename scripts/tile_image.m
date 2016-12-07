function tile_image (filename, out_dir, basename)

    delim = '_';
    % 600 x 400
    img = imread(filename);
    m_tiles = 0;
    k_tiles = 0;
    col_size = 60;
    row_size = 40;
    for m = 1:row_size:400
        k_tiles = 0; 
        for k = 1:col_size:600
            newimg = img(m:m+row_size-1, k:k+col_size-1, :);
            outfile = fullfile(out_dir, [basename delim num2str(m_tiles) delim num2str(k_tiles) '.bmp']);
            imwrite(newimg, outfile);
            k_tiles = k_tiles + 1;
        end
        m_tiles = m_tiles + 1;
    end
    
end
