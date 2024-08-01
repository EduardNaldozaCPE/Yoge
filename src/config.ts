import * as path from 'node:path';
import * as fs from 'fs';
import { cwd } from 'process';
import { config } from './dataTypes'

let landmarkerPath = 'resources/landmarker-config.json';

export const landmarkerConfig : config = JSON.parse(
    fs.readFileSync(
        path.join( cwd(), landmarkerPath ), 'utf8')
    );